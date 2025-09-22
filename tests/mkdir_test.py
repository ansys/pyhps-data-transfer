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

"""This module contains tests for verifying the creation of directories
using the Data Transfer API and Async Data Transfer API from the Ansys HPS Data Transfer Client.
"""

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models import OperationState, StoragePath


def test_mkdir(storage_path, client):
    """Test creating a directory."""
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

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == True


async def test_async_mkdir(storage_path, async_client):
    """Test creating a directory using the Async Data Transfer API."""
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

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == True
