"""
Example script for file operations.
"""

import asyncio
import glob
import logging
import os

from ansys.hps.data_transfer.client import AsyncClient, AsyncDataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath

log = logging.getLogger(__name__)


hps_url = "https://localhost:8443/hps"
dt_url = f"{hps_url}/dt/api/v1"
auth_url = f"{hps_url}/auth/realms/rep"

logger = logging.getLogger()
logging.basicConfig(format="%(asctime)s %(levelname)8s > %(message)s", level=logging.DEBUG)


async def main():
    token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    token = token.get("access_token", None)
    assert token is not None

    log.info("Connecting to the data transfer service client..")
    client = AsyncClient(clean=True)

    client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=token,
        data_transfer_url=dt_url,
    )
    await client.start()

    api = AsyncDataTransferApi(client)
    await api.status(wait=True)

    log.info("Query storages ...")
    storages = await api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]
    log.info(f"Available storages: {storage_names}")

    log.info("Creating a directory ...")
    base_dir = "basic-example"
    mkdir_op = await api.mkdir([StoragePath(path=f"{base_dir}")])
    await api.wait_for([mkdir_op.id])

    log.info("Copying files ...")
    files = glob.glob(os.path.join(os.path.dirname(__file__), "files", "*.txt"))
    srcs = [StoragePath(path=file, remote="local") for file in files]
    dsts = [StoragePath(path=f"{base_dir}/{os.path.basename(file)}") for file in files]

    op = await api.copy([SrcDst(src=src, dst=dst) for src, dst in zip(srcs, dsts)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

    files = glob.glob(os.path.join(os.path.dirname(__file__), "*.txt"))
    srcs = [StoragePath(path=file, remote="local") for file in files]
    dsts = [StoragePath(path=f"{os.path.basename(file)}") for file in files]

    op = await api.copy([SrcDst(src=src, dst=dst) for src, dst in zip(srcs, dsts)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

    log.info("Listing files ...")
    op = await api.list([StoragePath(path=base_dir)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")
    log.info(f"Files in {base_dir}: {op[0].result}")

    log.info("Getting metadata ...")
    op = await api.get_metadata([StoragePath(path=f"{base_dir}/2.txt")])
    op = await api.wait_for(op.id)
    md = op[0].result[f"{base_dir}/2.txt"]
    log.info(f"Metadata for {base_dir}/2.txt: {md}")

    log.info("Removing files ...")
    op = await api.rmdir([StoragePath(path=base_dir)])
    op = await api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
