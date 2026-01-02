# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""This module contains tests for verifying the retrieval and validation of metadata
associated with files and directories using the Data Transfer API and Async Data Transfer API
from the Ansys HPS Data Transfer Client.
"""

import logging
import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models import DataAssignment, OperationState, SrcDst, StoragePath

log = logging.getLogger(__name__)


def test_get_basic_metadata(storage_path, client):
    """Test retrieving basic metadata for a file."""
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    file_path = temp_file.name
    file_name = os.path.basename(file_path)

    src = StoragePath(path=file_path, remote="local")
    dst = StoragePath(path=f"{storage_path}/{file_name}")
    op = api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.get_metadata([dst])
    op = api.wait_for(op.id)[0]
    assert op.state == OperationState.Succeeded, op.messages
    md = op.result[dst.path]
    assert md is not None
    assert md["size"] == os.path.getsize(file_path)
    assert md["checksum"] != ""
    assert md["checksum"] == "ac2390bba2edaa01"


def test_set_custom_metadata(storage_path, client):
    """Test setting custom metadata for a file."""
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    file_path = temp_file.name
    file_name = os.path.basename(file_path)

    src = StoragePath(path=file_path, remote="local")
    dst = StoragePath(path=f"{storage_path}/{file_name}")
    op = api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    da = DataAssignment(custom={"test_val": "some value"})
    op = api.set_metadata({dst.path: da})
    op = api.wait_for(op.id)[0]
    assert op.state == OperationState.Succeeded, op.messages

    op = api.get_metadata([dst])
    op = api.wait_for(op.id)[0]
    assert op.state == OperationState.Succeeded, op.messages
    md = op.result[dst.path]
    assert md is not None
    assert md["size"] == os.path.getsize(file_path)
    assert md["checksum"] == "ac2390bba2edaa01"
    assert "test_val" in md["custom"]
    assert md["custom"]["test_val"] == "some value"


async def test_async_get_basic_metadata(storage_path, async_client):
    """Test retrieving basic metadata for a file using the Async Data Transfer API."""
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    file_path = temp_file.name
    file_name = os.path.basename(file_path)

    src = StoragePath(path=file_path, remote="local")
    dst = StoragePath(path=f"{storage_path}/{file_name}")
    op = await api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.get_metadata([dst])
    op = await api.wait_for(op.id)
    op = op[0]
    assert op.state == OperationState.Succeeded, op.messages
    md = op.result[dst.path]
    assert md is not None
    assert md["size"] == os.path.getsize(temp_file.name)
    assert md["checksum"] != ""
    assert md["checksum"] == "ac2390bba2edaa01"


async def test_async_set_custom_metadata(storage_path, async_client):
    """Test setting custom metadata for a file using the Async Data Transfer API."""
    api = AsyncDataTransferApi(async_client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")

    file_path = temp_file.name
    file_name = os.path.basename(file_path)

    src = StoragePath(path=file_path, remote="local")
    dst = StoragePath(path=f"{storage_path}/{file_name}")
    op = await api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    da = DataAssignment(custom={"test_val": "some value"})
    op = await api.set_metadata({dst.path: da})
    op = await api.wait_for(op.id)
    op = op[0]
    assert op.state == OperationState.Succeeded, op.messages

    op = await api.get_metadata([dst])
    op = await api.wait_for(op.id)
    op = op[0]
    assert op.state == OperationState.Succeeded, op.messages
    md = op.result[dst.path]
    assert md is not None
    assert md["size"] == os.path.getsize(file_path)
    assert md["checksum"] == "ac2390bba2edaa01"
    assert "test_val" in md["custom"]
    assert md["custom"]["test_val"] == "some value"
