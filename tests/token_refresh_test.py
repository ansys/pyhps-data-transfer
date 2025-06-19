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

"""This module contains tests for verifying the token refresh functionality
in the Ansys HPS data transfer client.
"""

import logging
import time

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate

log = logging.getLogger(__name__)


def test_token_passing(client, admin_token, auth_url):
    """Test passing a token to the client."""
    api = DataTransferApi(client)
    api.status(wait=True)

    expires_in = admin_token["expires_in"]
    log.info(f"Token expires in {expires_in} seconds")

    s = api.status()
    assert s.ready

    tk = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    client.binary_config.token = tk["access_token"]
    assert client.binary_config.token == tk["access_token"]
    expires_in = tk["expires_in"]
    log.info(f"Token expires in {expires_in} seconds")

    time.sleep(2)

    s = api.status()
    assert s.ready


async def test_async_token_passing(async_client, admin_token, auth_url):
    """Test passing a token to the async client."""
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    expires_in = admin_token["expires_in"]
    log.info(f"Token expires in {expires_in} seconds")

    s = await api.status()
    assert s.ready

    tk = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    async_client.binary_config.token = tk["access_token"]
    assert async_client.binary_config.token == tk["access_token"]

    time.sleep(2)

    s = await api.status()
    assert s.ready
