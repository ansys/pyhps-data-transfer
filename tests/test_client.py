import pytest
from unittest.mock import MagicMock, patch
import httpx
from ansys.hps.data_transfer.client.client import Client
from unittest.mock import AsyncMock, MagicMock
from ansys.hps.data_transfer.client.client import AsyncClient

@pytest.fixture
def mock_client():
    """Fixture to create a mock Client instance."""
    client = Client()
    client._unauthorized_max_retry = 2
    client._unauthorized_num_retry = 0
    client._bin_config = MagicMock()
    client._session = MagicMock()
    client.refresh_token_callback = MagicMock(return_value="new_token")
    return client

def test_auto_refresh_token_success(mock_client):
    """Test _auto_refresh_token when token refresh is successful."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"
    
    retried_response = MagicMock(spec=httpx.Response)
    retried_response.status_code = 200
    retried_response.content = b"retried content"
    mock_client._session.send.return_value = retried_response

    mock_client._auto_refresh_token(response)

    # Verify token refresh callback was called
    mock_client.refresh_token_callback.assert_called_once()

    # Verify Authorization header was updated
    assert response.request.headers["Authorization"] == "Bearer new_token"

    # Verify the retried response content and status code were updated
    assert response._content == b"retried content"
    assert response.status_code == 200

def test_auto_refresh_token_no_callback(mock_client):
    """Test _auto_refresh_token when no refresh callback is provided."""
    mock_client.refresh_token_callback = None

    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"

    mock_client._auto_refresh_token(response)

    # Verify token refresh callback was not called
    assert mock_client.refresh_token_callback is None

    # Verify no changes were made to the response
    assert response.status_code == 401
    assert "_content" not in response.__dict__

def test_auto_refresh_token_exceeds_retry_limit(mock_client):
    """Test _auto_refresh_token when retry limit is exceeded."""
    mock_client._unauthorized_num_retry = 2  # Set retries to max

    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"

    mock_client._auto_refresh_token(response)

    # Verify token refresh callback was not called
    mock_client.refresh_token_callback.assert_not_called()

    # Verify no changes were made to the response
    assert response.status_code == 401
    assert "_content" not in response.__dict__

def test_auto_refresh_token_non_401_response(mock_client):
    """Test _auto_refresh_token when response status is not 401."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"

    mock_client._auto_refresh_token(response)

    # Verify token refresh callback was not called
    mock_client.refresh_token_callback.assert_not_called()

    # Verify no changes were made to the response
    assert response.status_code == 200
    assert "_content" not in response.__dict__

@pytest.fixture
def mock_async_client():
    """Fixture to create a mock AsyncClient instance."""
    client = AsyncClient()
    client._unauthorized_max_retry = 2
    client._unauthorized_num_retry = 0
    client._bin_config = MagicMock()
    client._session = AsyncMock()
    client.refresh_token_callback = AsyncMock(return_value="new_async_token")
    return client

@pytest.mark.asyncio
async def test_async_auto_refresh_token_success(mock_async_client):
    """Test _async_auto_refresh_token when token refresh is successful."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"
    
    retried_response = MagicMock(spec=httpx.Response)
    retried_response.status_code = 200
    retried_response.content = b"retried async content"
    mock_async_client._session.send.return_value = retried_response

    await mock_async_client._async_auto_refresh_token(response)

    # Verify token refresh callback was called
    mock_async_client.refresh_token_callback.assert_awaited_once()

    # Verify Authorization header was updated
    assert response.request.headers["Authorization"] == "Bearer new_async_token"

    # Verify the retried response content and status code were updated
    assert response._content == b"retried async content"
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_async_auto_refresh_token_no_callback(mock_async_client):
    """Test _async_auto_refresh_token when no refresh callback is provided."""
    mock_async_client.refresh_token_callback = None

    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"

    await mock_async_client._async_auto_refresh_token(response)

    # Verify token refresh callback was not called
    assert mock_async_client.refresh_token_callback is None

    # Verify no changes were made to the response
    assert response.status_code == 401
    assert "_content" not in response.__dict__

@pytest.mark.asyncio
async def test_async_auto_refresh_token_exceeds_retry_limit(mock_async_client):
    """Test _async_auto_refresh_token when retry limit is exceeded."""
    mock_async_client._unauthorized_num_retry = 2  # Set retries to max

    response = MagicMock(spec=httpx.Response)
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"

    await mock_async_client._async_auto_refresh_token(response)

    # Verify token refresh callback was not called
    mock_async_client.refresh_token_callback.assert_not_called()

    # Verify no changes were made to the response
    assert response.status_code == 401
    assert "_content" not in response.__dict__

@pytest.mark.asyncio
async def test_async_auto_refresh_token_non_401_response(mock_async_client):
    """Test _async_auto_refresh_token when response status is not 401."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.request = MagicMock()
    response.request.headers = {}
    response.request.method = "GET"
    response.request.url = "https://example.com"

    await mock_async_client._async_auto_refresh_token(response)

    # Verify token refresh callback was not called
    mock_async_client.refresh_token_callback.assert_not_called()

    # Verify no changes were made to the response
    assert response.status_code == 200
    assert "_content" not in response.__dict__
