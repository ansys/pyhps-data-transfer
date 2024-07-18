"""
Example script for file operations.
"""
import glob
import logging
import os

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

    log.info("Query storages ...")
    storages = api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]
    log.info(f"Available storages: {storage_names}")

    log.info("Creating a directory ...")
    base_dir = "basic-example"
    mkdir_op = api.mkdir([StoragePath(path=f"{base_dir}/")])
    api.wait_for([mkdir_op.id])

    log.info("Copying files ...")
    files = glob.glob(os.path.join(os.path.dirname(__file__), "files", "*.txt"))
    srcs = [StoragePath(path=file, remote="local") for file in files]
    dsts = [StoragePath(path=f"{base_dir}/{os.path.basename(file)}") for file in files]

    op = api.copy([SrcDst(src=src, dst=dst) for src, dst in zip(srcs, dsts)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

    log.info("Listing files ...")
    op = api.list([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")
    log.info(f"Files in {base_dir}: {op[0].result}")

    log.info("Removing files ...")
    op = api.rmdir([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

    client.stop()
