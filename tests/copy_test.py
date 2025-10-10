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

"""This module contains tests for verifying file copy operations using the
Data Transfer API and Async Data Transfer API from the Ansys HPS Data Transfer Client.

The tests ensure that files are copied correctly between local and remote locations,
and validate the integrity of the copied files using file comparison utilities.
"""

import filecmp
import logging
import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models import OperationState, SrcDst, StoragePath

log = logging.getLogger(__name__)


def test_copy(storage_path, client):
    """Test copying a file from local to remote storage and back."""
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{storage_path}/{temp_file_name}")
    op = api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    src = dst
    dst = StoragePath(path=os.path.join(os.getcwd(), "downloaded.txt"), remote="local")
    op = api.copy([SrcDst(src=src, dst=dst)])
    op = api.wait_for([op])
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert filecmp.cmp(temp_file.name, dst.path, shallow=False)


async def test_async_copy(storage_path, async_client):
    """Test copying a file from local to remote storage and
    back using the Async Data Transfer API.
    """
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{storage_path}/{temp_file_name}")
    op = await api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    src = dst
    dst = StoragePath(path=os.path.join(os.getcwd(), "downloaded.txt"), remote="local")
    op = await api.copy([SrcDst(src=src, dst=dst)])
    op = await api.wait_for([op])
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert filecmp.cmp(temp_file.name, dst.path, shallow=False)


def test_copy_empty_file(storage_path, client):
    """Test copying an empty file from local to remote storage."""
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        pass
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{storage_path}/{temp_file_name}")
    op = api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
