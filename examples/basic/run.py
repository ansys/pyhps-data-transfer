"""
Example script for file operations.
"""
import logging
import os
import pathlib
import uuid

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

    user_token = authenticate(username="repuser", password="repuser", verify=False, url=auth_url)
    user_token = user_token.get("access_token", None)
    assert user_token is not None

    log.info("Connecting to the data transfer service client..")
    client = Client()

    client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=user_token,
        data_transfer_url=dt_url,
    )
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)

    log.info("Query storages..")
    storages = api.storages()
    s3_remote = storages[0].get("name", "any")
    local_remote = "local"

    log.info("Creating a directory..")
    bucket = str(uuid.uuid4())
    mkdir_op = api.mkdir([StoragePath(path=f"{bucket}/", remote=f"{s3_remote}")])
    api.wait_for([mkdir_op.id])

    log.info("Uploading files..")
    upload_path = pathlib.Path(__file__).parent / "files"
    for file in os.listdir(f"{upload_path}"):
        full_path = os.path.abspath(f"{upload_path}/{file}")
        upload_op = api.upload_file(remote=s3_remote, path=f"{bucket}/{file}", file_path=full_path)
        api.wait_for([upload_op.id])

    log.info("Moving files..")
    new_bucket = str(uuid.uuid4())
    list_op = api.list([StoragePath(path=f"{bucket}/", remote=f"{s3_remote}")])
    list_op_resp = api.wait_for([list_op.id])

    move_items = []
    for file in list_op_resp[0].result[f"{s3_remote}:{bucket}/"]:
        move_items.append(
            SrcDst(
                src=StoragePath(path=f"{bucket}/{file}", remote=s3_remote),
                dst=StoragePath(path=f"{new_bucket}/{file}", remote=s3_remote),
            )
        )
    move_op = api.move(move_items)
    api.wait_for([move_op.id], timeout=60)

    log.info("Copying files..")
    list_op = api.list([StoragePath(path=f"{new_bucket}/", remote=f"{s3_remote}")])
    list_op_resp = api.wait_for([list_op.id])
    copy_items = []
    for file in list_op_resp[0].result[f"{s3_remote}:{new_bucket}/"]:
        copy_items.append(
            SrcDst(
                src=StoragePath(path=f"{bucket}/{file}", remote=s3_remote),
                dst=StoragePath(path=f"{file}", remote=local_remote),
            )
        )
    copy_op = api.copy(copy_items)
    api.wait_for([copy_op.id], timeout=60)

    log.info("Downloading files..")
    list_op = api.list([StoragePath(path=f"", remote=f"{local_remote}")])
    list_op_resp = api.wait_for([list_op.id])
    for file in list_op_resp[0].result[f"{local_remote}:/"]:
        download_op = api.download_file(path=f"{bucket}/{file}", remote=f"{s3_remote}")
        api.wait_for([download_op.id])
