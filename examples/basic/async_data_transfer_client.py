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
.. _ref_async:

=========
Run Async
=========

This script is intended to be run from the command line, where it will
authenticate with the specified HPS service and set up an asynchronous
client for data transfer operations, transfer files to and from remote backends
using the data transfer service.

Example usage:
``python examples/async_data_transfer_client.py --url "https://example.com/hps" --username "user" --password "pass"``
"""

import asyncio
import glob
import logging
import os

import typer
from typing_extensions import Annotated

from ansys.hps.data_transfer.client import AsyncClient, AsyncDataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath

log = logging.getLogger(__name__)
logger = logging.getLogger()
logging.basicConfig(format="%(asctime)s %(levelname)8s > %(message)s", level=logging.DEBUG)


async def main(
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
    url: Annotated[str, typer.Option(help="HPS URL to connect to")] = "https://localhost:8443/hps",
    username: Annotated[str, typer.Option(help="Username to authenticate with")] = "repadmin",
    password: Annotated[
        str, typer.Option(prompt=True, hide_input=True, help="Password to authenticate with")
    ] = "repadmin",
):

    dt_url = f"{url}/dt/api/v1"
    auth_url = f"{url}/auth/realms/rep"
    token = authenticate(username=username, password=password, verify=False, url=auth_url)
    token = token.get("access_token", None)
    assert token is not None

########################################
# Create an ``AsyncClient`` instance
# ==================================

    client = AsyncClient(clean=True)

    client.binary_config.update(
        verbosity=3,
        debug=debug,
        insecure=True,
        token=token,
        data_transfer_url=dt_url,
    )
    await client.start()

########################################
# Create an ``AsyncDataTransferApi`` instance
# ===========================================


    api = AsyncDataTransferApi(client)
    await api.status(wait=True)

########################################
# Get available storages
# ======================
    storages = await api.storages()
    storage_names = [f"{storage['name']}({storage['type']})" for storage in storages]
    log.info(f"Available storages: {storage_names}")

#################
# Perform file operations
# =======================

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
