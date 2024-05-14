"""
Example script for file operations.
"""
import logging

from ansys.hps.dt_client.data_transfer import Client, HPSError

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
            log.info("Creating a directory..")
            log.info("Uploading files..")
            log.info("Moving files..")
            log.info("Copying files..")
            log.info("Downloading files..")
    except HPSError as e:
        log.error(str(e))
