"""This module contains tests for verifying the functionality of securing 
 the communication between the client and worker using an API key.
"""
import pytest
from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client import ClientError

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