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

"""This module contains tests for verifying the functionality of removing directories
using the Data Transfer API and Async Data Transfer API from the Ansys HPS Data Transfer Client.
"""

import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState


def test_rmdir(storage_path, client):
    """Test removing a directory."""
    api = DataTransferApi(client)
    api.status(wait=True)

    dst = StoragePath(path=f"{storage_path}/a/b")

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == False

    op = api.mkdir([dst])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    op = api.copy(
        [
            SrcDst(
                src=StoragePath(path=temp_file.name, remote="local"),
                dst=StoragePath(path=f"{dst.path}/{temp_file_name}"),
            )
        ]
    )
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == True

    op = api.rmdir([dst])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == False


async def test_async_rmdir(storage_path, async_client):
    """Test removing a directory using the async API."""
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    dst = StoragePath(path=f"{storage_path}/a/b")

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == False

    op = await api.mkdir([dst])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    op = await api.copy(
        [
            SrcDst(
                src=StoragePath(path=temp_file.name, remote="local"),
                dst=StoragePath(path=f"{dst.path}/{temp_file_name}"),
            )
        ]
    )
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == True

    op = await api.rmdir([dst])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == False
