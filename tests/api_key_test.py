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

"""This module contains tests for verifying the functionality of securing
the communication between the client and worker using an API key.
"""

import pytest

from ansys.hps.data_transfer.client import AsyncDataTransferApi, ClientError, DataTransferApi


def test_api_key(client):
    """Test getting the status of the client."""

    if not client.has("auth_types.api_key"):
        pytest.skip("API key authentication is not available in this build.")

    api = DataTransferApi(client)
    api.status(wait=True)
    resp = api.storages()
    assert resp is not None

    # Use an invalid value as the API key
    old_api_key = client._session.headers[client._api_key_header]
    client._session.headers[client._api_key_header] = "whatever"
    with pytest.raises(ClientError):
        resp = api.storages()

    # Restore the original API key
    client._session.headers[client._api_key_header] = old_api_key


async def test_async_api_key(async_client):
    """Test getting the status of the async client."""

    if not async_client.has("auth_types.api_key"):
        pytest.skip("API key authentication is not available in this build.")

    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)
    resp = await api.storages()
    assert resp is not None

    # Use an invalid value as the API key
    old_api_key = async_client._session.headers[async_client._api_key_header]
    async_client._session.headers[async_client._api_key_header] = "whatever"
    with pytest.raises(ClientError):
        await api.storages()

    # Restore the original API key
    async_client._session.headers[async_client._api_key_header] = old_api_key
