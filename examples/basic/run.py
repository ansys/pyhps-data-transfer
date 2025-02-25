# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Example script for file operations.
"""

import glob
import logging
import os

from ansys.hps.data_transfer.client import Client, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from tests.utils import authenticate

log = logging.getLogger(__name__)


hps_url = "https://localhost:8443/hps"
dt_url = f"{hps_url}/dt/api/v1"
auth_url = f"{hps_url}/auth/realms/rep"


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(asctime)s %(levelname)8s > %(message)s", level=logging.DEBUG)

    token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    token = token.get("access_token", None)
    assert token is not None

    log.info("Connecting to the data transfer service client..")
    client = Client()

    client.binary_config.update(verbosity=3, debug=True, insecure=True, token=token, data_transfer_url=dt_url, log=True)
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)

    log.info("Query storages ...")
    storages = api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]
    log.info(f"Available storages: {storage_names}")

    log.info("Creating a directory ...")
    base_dir = "basic-example"
    mkdir_op = api.mkdir([StoragePath(path=f"{base_dir}")])
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

    log.info("Getting metadata ...")
    op = api.get_metadata([StoragePath(path=f"{base_dir}/2.txt")])
    op = api.wait_for(op.id)
    md = op[0].result[f"{base_dir}/2.txt"]
    log.info(f"Metadata for {base_dir}/2.txt: {md}")

    log.info("Removing files ...")
    op = api.rmdir([StoragePath(path=base_dir)])
    op = api.wait_for([op.id])
    log.info(f"Operation {op[0].state}")

    client.stop()
