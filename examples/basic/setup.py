"""
Example script for file operations.
"""
import logging
import uuid

from ansys.hps.dt_client.data_transfer import Client, DataTransferApi, HPSError
from ansys.hps.dt_client.data_transfer.models.rest import StoragePath

log = logging.getLogger(__name__)

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
        ) as api_client:

            dts_api = DataTransferApi(api_client)

            log.info("Query storages..")
            storages = dts_api.storages()

            log.info("Creating a directory..")
            bucket = str(uuid.uuid4())
            dts_api.mkdir([StoragePath(path=f"{bucket}/", remote=f"{storages[0].name}")])

            log.info("Uploading files..")
            log.info("Moving files..")
            log.info("Copying files..")
            log.info("Downloading files..")
    except HPSError as e:
        log.error(str(e))
