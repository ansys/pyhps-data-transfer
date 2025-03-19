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

"""This module contains tests for verifying the performance and reliability of
large batch file operations using the Data Transfer API and Async Data Transfer API
from the Ansys HPS Data Transfer Client."""

import logging
import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

log = logging.getLogger(__name__)

num_copies = 200
content = "Mock file; " * 100


def test_large_batch(storage_path, client):
    """Test copying a large batch of files from local to remote storage."""
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(content)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []

    for i in range(num_copies):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    op = api.copy(dsts)
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages


async def test_async_large_batch(storage_path, async_client):
    """Test copying a large batch of files from local to remote
    using the AsyncDataTransferApi"""
    api = AsyncDataTransferApi(async_client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(content)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []

    for i in range(num_copies):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    op = await api.copy(dsts)
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
