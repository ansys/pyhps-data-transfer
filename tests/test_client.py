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

"""This module contains tests for verifying the functionality of the Client class"""

import unittest
from unittest.mock import MagicMock, mock_open, patch

from ansys.hps.data_transfer.client.client import ClientBase


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
        mock_open_file.assert_called_once_with("/path/to/panic_file.log", "r")
        mock_log.error.assert_any_call("Worker panic file content:\nError: Something went wrong\n")
        mock_log.error.assert_any_call("Worker panic file content:\nDetails: Invalid configuration\n")


if __name__ == "__main__":
    unittest.main()
