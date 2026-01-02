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

import unittest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

from ansys.hps.data_transfer.client.client import AsyncClient, Client, ClientBase


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


"""This module contains tests for verifying the functionality of the Client class"""


class TestClientBase(unittest.TestCase):
    """Test suite for the ClientBase class."""

    def setUp(self):
        """Set up the ClientBase instance for testing."""
        self.client = ClientBase()
        self.client.panic_file = None

    @patch("ansys.hps.data_transfer.client.client.log")
    def test_fetch_panic_file(self, mock_log):
        """Test the _fetch_panic_file method."""
        # Mock the response object
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"debug": {"panic_file": "/path/to/panic_file.log"}}

        # Call the method
        self.client._fetch_panic_file(mock_resp)

        # Assertions
        assert self.client.panic_file == "/path/to/panic_file.log"
        mock_log.debug.assert_called_with("Worker panic file: /path/to/panic_file.log")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=100)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="Error: Something went wrong\n\nDetails: Invalid configuration\n\n",
    )
    @patch("ansys.hps.data_transfer.client.client.log")
    def test_panic_file_contents(self, mock_log, mock_open_file, mock_getsize, mock_exists):
        """Test the _panic_file_contents method."""
        # Set the panic file path
        self.client.panic_file = "/path/to/panic_file.log"

        # Call the method
        self.client._panic_file_contents()

        # Assertions
        mock_exists.assert_called_once_with("/path/to/panic_file.log")
        mock_getsize.assert_called_once_with("/path/to/panic_file.log")
        mock_log.error.assert_any_call("Worker panic file content:\nError: Something went wrong\n")
        mock_log.error.assert_any_call("Worker panic file content:\nDetails: Invalid configuration\n")


if __name__ == "__main__":
    unittest.main()
