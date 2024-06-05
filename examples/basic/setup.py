"""
Example script for file operations.
"""
import logging
import os
import pathlib
import time
import uuid

from ansys.hps.dt_client.data_transfer import Client, DataTransferApi, HPSError
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState

log = logging.getLogger(__name__)


def await_operation_completion(api: DataTransferApi, operation_id: str, max_attempts: int = 10):
    for _ in range(max_attempts):
        time.sleep(1)
        resp = api.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            return resp
    raise HPSError("Exceeded max number of attempts for operation to complete")


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    try:
        log.info("Connecting to the data transfer service client..")
        with Client(
            data_transfer_url="https://localhost:8443/hps/dts/api/v1",
            external_url="http://localhost:1091",
            run_client_binary=True,
            binary_path=".\\bin\\hpsdata.exe",
        ) as client:

            api = DataTransferApi(client)

            log.info("Query storages..")
            storages = api.storages()
            s3_remote = storages[0].get("name", "any")
            local_remote = "local"

            log.info("Creating a directory..")
            bucket = str(uuid.uuid4())
            mkdir_op = api.mkdir([StoragePath(path=f"{bucket}/", remote=f"{s3_remote}")])
            await_operation_completion(api, mkdir_op.id)

            log.info("Uploading files..")
            upload_path = pathlib.Path(__file__).parent / "files"
            for file in os.listdir(f"{upload_path}"):
                full_path = os.path.abspath(f"{upload_path}/{file}")
                upload_op = api.upload_file(remote=s3_remote, path=f"{bucket}/{file}", file_path=full_path)
                await_operation_completion(api, upload_op.id)

            log.info("Moving files..")
            new_bucket = str(uuid.uuid4())
            list_op = api.list([StoragePath(path=f"{bucket}/", remote=f"{s3_remote}")])
            list_op_resp = await_operation_completion(api, list_op.id)
            move_items = []
            for file in list_op_resp[0].result[f"{s3_remote}:{bucket}/"]:
                move_items.append(
                    SrcDst(
                        src=StoragePath(path=f"{bucket}/{file}", remote=s3_remote),
                        dst=StoragePath(path=f"{new_bucket}/{file}", remote=s3_remote),
                    )
                )
            move_op = api.move(move_items)
            await_operation_completion(api, move_op.id, 60)

            log.info("Copying files..")
            list_op = api.list([StoragePath(path=f"{new_bucket}/", remote=f"{s3_remote}")])
            list_op_resp = await_operation_completion(api, list_op.id)
            copy_items = []
            for file in list_op_resp[0].result[f"{s3_remote}:{new_bucket}/"]:
                copy_items.append(
                    SrcDst(
                        src=StoragePath(path=f"{bucket}/{file}", remote=s3_remote),
                        dst=StoragePath(path=f"{file}", remote=local_remote),
                    )
                )
            copy_op = api.copy(copy_items)
            await_operation_completion(api, copy_op.id, 60)

            log.info("Downloading files..")
            list_op = api.list([StoragePath(path=f"", remote=f"{local_remote}")])
            list_op_resp = await_operation_completion(api, list_op)
            for file in list_op_resp[0].result[f"{local_remote}:/"]:
                download_op = api.download_file(path=f"{bucket}/{file}", remote=f"{s3_remote}")
                await_operation_completion(api, download_op)

    except HPSError as e:
        log.error(str(e))
