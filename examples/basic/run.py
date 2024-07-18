"""
Example script for file operations.
"""
import logging
import os
import pathlib

from ansys.hps.dt_client.data_transfer import Client, DataTransferApi
from ansys.hps.dt_client.data_transfer.authenticate import authenticate
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath

log = logging.getLogger(__name__)


hps_url = "https://localhost:8443/hps"
dt_url = f"{hps_url}/dt/api/v1"
auth_url = f"{hps_url}/auth/realms/rep"


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    token = token.get("access_token", None)
    assert token is not None

    log.info("Connecting to the data transfer service client..")
    client = Client()

    client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=token,
        data_transfer_url=dt_url,
    )
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)

    log.info("Query storages..")
    storages = api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]
    log.info(f"Available storages: {storage_names}")
    local_remote = "local"

    log.info("Creating a directory..")
    base_dir = "basic_example"
    mkdir_op = api.mkdir([StoragePath(path=f"{base_dir}/")])
    api.wait_for([mkdir_op.id])

    log.info("Uploading files..")
    upload_path = pathlib.Path(__file__).parent / "files"
    for file in os.listdir(f"{upload_path}"):
        full_path = os.path.abspath(f"{upload_path}/{file}")
        upload_op = api.upload_file(dst=f"{base_dir}/{file}", src=full_path)
        api.wait_for([upload_op.id])

    log.info("Moving files..")
    new_base_dir = f"{base_dir}/moved"
    list_op = api.list([StoragePath(path=f"{base_dir}/")])
    list_op_resp = api.wait_for([list_op.id])

    move_items = []
    log.warning(list_op_resp)
    for file in list_op_resp[0].result[f"any:{base_dir}/"]:
        move_items.append(
            SrcDst(
                src=StoragePath(path=f"{base_dir}/{file}"),
                dst=StoragePath(path=f"{new_base_dir}/{file}"),
            )
        )
    move_op = api.move(move_items)
    api.wait_for([move_op.id], timeout=60)

    log.info("Copying files..")
    list_op = api.list([StoragePath(path=f"{new_base_dir}/")])
    list_op_resp = api.wait_for([list_op.id])
    copy_items = []
    for file in list_op_resp[0].result[f"{s3_remote}:{new_base_dir}/"]:
        copy_items.append(
            SrcDst(
                src=StoragePath(path=f"{base_dir}/{file}"),
                dst=StoragePath(path=f"{file}", remote=local_remote),
            )
        )
    copy_op = api.copy(copy_items)
    api.wait_for([copy_op.id], timeout=60)

    log.info("Downloading files..")
    list_op = api.list([StoragePath(path=f"", remote=f"{local_remote}")])
    list_op_resp = api.wait_for([list_op.id])
    for file in list_op_resp[0].result[f"{local_remote}:/"]:
        download_op = api.download_file(src=f"{base_dir}/{file}", dst=file)
        api.wait_for([download_op.id])

    client.stop()
