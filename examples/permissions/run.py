import logging
import os
import pathlib
import traceback

from keycloak import KeycloakAdmin

from ansys.hps.dt_client.data_transfer import Client, DataTransferApi
from ansys.hps.dt_client.data_transfer.authenticate import authenticate
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath
from ansys.hps.dt_client.data_transfer.models.permissions import (
    Resource,
    ResourceType,
    RoleAssignment,
    RoleQuery,
    RoleType,
    Subject,
    SubjectType,
)

stream_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s", datefmt="%H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.DEBUG)
log = logging.getLogger("ansys.hps")
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)


hps_url = "https://localhost:8443/hps"
keycloak_url = f"{hps_url}/auth"
auth_url = f"{keycloak_url}/realms/rep"
dt_url = f"{hps_url}/dt/api/v1"


def get_user_id_from_keycloak():
    admin = KeycloakAdmin(
        server_url=keycloak_url + "/",
        username="keycloak",
        password="keycloak123",
        realm_name="rep",
        user_realm_name="master",
        verify=False,
    )
    user_id = admin.get_user_id("repuser")
    return user_id


if __name__ == "__main__":
    run_bin = True

    log.info("Logging in as repuser ...")
    user_token = authenticate(username="repuser", password="repuser", verify=False, url=auth_url)
    user_token = user_token.get("access_token", None)

    log.info("Preparing data transfer client for 'repuser' ...")
    user = DataTransferApi(
        Client(data_transfer_url=dt_url, run_client_binary=run_bin, token=user_token, port=1091, verify=False)
    )
    user.start()

    log.info("Checking binary's status ...")
    status = user.status(wait=True)
    log.info(f"User status: {status}")

    source_dir = pathlib.Path(__file__).parent / "files"
    source_dir = os.path.relpath(source_dir, os.getcwd())
    log.info(f"Searching for files to copy in {source_dir} ...")
    files = [os.path.join(source_dir, f) for f in os.listdir(f"{source_dir}")]
    log.info("Found files:")
    for file in files:
        log.info(f"- {file}")

    log.info("Trying to copy files as 'repuser'...")
    target_dir = "my_permissions_demo_dir"
    src_dst = [
        SrcDst(
            src=StoragePath(path=f, remote="local"),
            dst=StoragePath(path=os.path.join(target_dir, os.path.basename(f)), remote="any"),
        )
        for f in files
    ]
    try:
        # The operation will fail because 'repuser' does not have the necessary permissions
        resp = user.copy(src_dst)
    except Exception as ex:
        log.error(f"Encountered error: {ex}")

    admin_token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    admin_token = admin_token.get("access_token", None)

    log.info("Preparing data transfer client for 'repadmin' ...")
    admin = DataTransferApi(
        Client(data_transfer_url=dt_url, run_client_binary=run_bin, token=admin_token, port=1091, verify=False)
    )
    admin.start()

    log.info("Granting 'repuser' the necessary permissions ...")
    user_id = get_user_id_from_keycloak()

    try:
        admin.set_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )
    except Exception as ex:
        log.info(ex)

    try:
        log.info("Verifying permissions for 'repuser' ...")
        resp = admin.check_permissions(
            [
                RoleQuery(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )

        log.info(f"Is 'repuser'({user_id}) allowed to read from {target_dir}? -> {resp.allowed}")

        log.info("Trying to copy files as 'repuser' one more time...")
        resp = user.copy(src_dst)
        op = user.wait_for([resp.id], timeout=10)[0]
        log.info(f"Copy operation state: {op.state}")

        log.info("Listing files in the target directory as 'repadmin' ...")
        resp = admin.list([StoragePath(path=target_dir, remote="any")])
        op = user.wait_for([resp.id], timeout=10)[0]
        log.info(f"Result: {op.result}")
    except Exception as ex:
        log.debug(traceback.format_exc())
        log.error(f"Error: {ex}")
    finally:
        log.info("Removing permissions for 'repuser' ...")
        admin.remove_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role="writer",
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )

    log.info("And that's all folks!")

    admin.stop()
    user.stop()
