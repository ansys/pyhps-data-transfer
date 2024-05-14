"""
Example script for file operations.
"""
import logging
import os
import uuid
import time

from ansys.hps.dt_client.data_transfer import Client, DataTransferApi, HPSError
from ansys.hps.dt_client.data_transfer.models.ops import OperationState
from ansys.hps.dt_client.data_transfer.models.rest import SrcDst, StoragePath

log = logging.getLogger(__name__)

def await_operation_completion(api: DataTransferApi, operation_id: str, max_attempts: int = 10):
    for _ in range(max_attempts):
        time.sleep(1)
        resp = api.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            return resp
    raise HPSError('Exceeded max number of attempts for operation to complete')

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    try:
        log.info("Connecting to the data transfer service client..")
        with Client(
            data_transfer_url="https://localhost:8443/hps/dts/api/v1",
            external_url=None,
            run_client_binary=True,
            binary_path=".\\bin\\hpsdata.exe",
        ) as client:

            api = DataTransferApi(client)

            log.info("Query storages..")
            storages = api.storages()
            remote = storages[0].get('name', 'any')

            log.info("Creating a directory..")
            bucket = str(uuid.uuid4())
            mkdir_op = api.mkdir([StoragePath(path=f"{bucket}/", remote=f"{remote}")])
            await_operation_completion(api, mkdir_op.id)

            log.info("Uploading files..")
            for file in os.listdir('./numbers'):
                full_path = os.path.abspath(f"./numbers/{file}")
                upload_op = api.upload_file(remote=remote, path=f"{bucket}/{file}", file_path=full_path)
                await_operation_completion(api, upload_op)
            

            log.info("Moving files..")
                

            log.info("Copying files..")

            log.info("Downloading files..")
            list_op = api.list([StoragePath(path=f"{bucket}/", remote=f"{remote}")])
            list_op_resp = await_operation_completion(api, list_op)
            for file in list_op_resp[0].children:
                download_op = api.download_file(path=f"{bucket}/{file}", remote=f"{remote}")
                await_operation_completion(api, download_op)

    except HPSError as e:
        log.error(str(e))
