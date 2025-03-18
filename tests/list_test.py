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

"""This module contains tests for verifying the functionality of listing files and directories
using the Data Transfer API from the Ansys HPS Data Transfer Client.
"""

import logging
import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

log = logging.getLogger(__name__)


def test_list(storage_path, client):
    """Test listing files in a directory."""
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    names = ["file_1", "file_2"]

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = [StoragePath(path=f"{storage_path}/{name}") for name in names]
    op = api.copy([SrcDst(src=src, dst=dst) for dst in dsts])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.list([StoragePath(path=storage_path)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    result = next(iter(op[0].result.values()))
    assert names[0] in result
    assert names[1] in result


async def test_async_list(storage_path, async_client):
    """Test listing files in a directory using the AsyncDataTransferApi."""
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    names = ["file_1", "file_2"]

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = [StoragePath(path=f"{storage_path}/{name}") for name in names]
    op = await api.copy([SrcDst(src=src, dst=dst) for dst in dsts])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.list([StoragePath(path=storage_path)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    result = next(iter(op[0].result.values()))
    assert names[0] in result
    assert names[1] in result
