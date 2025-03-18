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

"""Module contains tests for verifying the functionality of retrieving the status 
of the Data Transfer API and Async Data Transfer API from the Ansys HPS Data Transfer Client.
"""

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi


def test_status(client):
    """Test getting the status of the client."""
    api = DataTransferApi(client)
    api.status(wait=True)
    resp = api.status()
    assert resp.build_info is not None


async def test_async_status(async_client):
    """Test getting the status of the async client."""
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)
    resp = await api.status()
    assert resp.build_info is not None
