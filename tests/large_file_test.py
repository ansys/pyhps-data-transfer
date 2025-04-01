# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

"""This module contains tests for verifying the performance, reliability, and correctness
of transferring large files using the Data Transfer API and Async Data Transfer API
from the Ansys HPS Data Transfer Client.
"""

import logging
import os
import tempfile
import time

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

log = logging.getLogger(__name__)

num_files = 2


def write_file(file_name, size):
    """Write a file with random data."""
    start_time = time.time()
    log.info(f"Generating file {file_name} with size {size} GB")
    gb1 = 1024 * 1024 * 1024  # 1GB
    with open(file_name, "wb") as fout:
        for _i in range(size):
            fout.write(os.urandom(gb1))
    log.info(f"File {file_name} has been generated after {(time.time() - start_time):.2f} seconds")
    return 0


def sync_copy(storage_path, api, file_size=5):
    """copying a large file to a remote storage."""
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        write_file(temp_file.name, file_size)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []
    for i in range(num_files):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    log.info("Starting copy ...")
    op = api.copy(dsts)
    return op


async def async_copy(storage_path, api, file_size=5):
    """copying a large file to a remote storage using the AsyncDataTransferApi."""
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        write_file(temp_file.name, file_size)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []
    for i in range(num_files):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    log.info("Starting copy ...")
    op = await api.copy(dsts)
    return op


def test_large_batch(storage_path, client):
    """Test copying a large file to a remote storage."""
    api = DataTransferApi(client)
    op = sync_copy(storage_path, api)
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages


def test_batch_with_wait_parameters(storage_path, client):
    """Test copying a large file to a remote storage."""
    api = DataTransferApi(client)
    log.info("Copy with progress handler")
    op = sync_copy(storage_path, api, 1)
    assert op.id is not None

    # test progress handler
    def handler(current_progress):
        log.info(f"{current_progress * 100.0}% completed")

    op = api.wait_for(op.id, progress_handler=handler)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    # test without streaming
    log.info("Copy without streaming")
    op = sync_copy(storage_path, api, 1)
    assert op.id is not None
    op = api.wait_for(op.id, stream=False)
    assert op[0].state == OperationState.Succeeded, op[0].messages


async def test_async_large_batch(storage_path, async_client):
    """Test copying a large file to a remote storage using the AsyncDataTransferApi."""
    api = AsyncDataTransferApi(async_client)
    op = await async_copy(storage_path, api)
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages


async def test_async_batch_with_wait_parameters(storage_path, async_client):
    """Test copying a large file to a remote storage using the AsyncDataTransferApi."""
    api = AsyncDataTransferApi(async_client)
    log.info("Copy with progress handler")
    op = await async_copy(storage_path, api, 1)
    assert op.id is not None

    # test progress handler
    def handler(current_progress):
        log.info(f"{current_progress * 100.0}% completed")

    op = await api.wait_for(op.id, progress_handler=handler)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    # test without streaming
    log.info("Copy without streaming")
    op = await async_copy(storage_path, api, 1)
    assert op.id is not None
    op = await api.wait_for(op.id, stream=False)
    assert op[0].state == OperationState.Succeeded, op[0].messages
