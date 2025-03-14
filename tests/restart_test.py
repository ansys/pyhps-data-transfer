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

import asyncio
import logging
import time

import psutil

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi

log = logging.getLogger(__name__)


def test_restart(client):
    # Let it start up
    api = DataTransferApi(client)
    api.status(wait=True)

    time.sleep(0.2)

    # Kill the binary and wait for it to restart
    p = psutil.Process(client.binary._process.pid)
    p.kill()
    time.sleep(0.2)
    # assert client.binary._process.poll() is not None

    api.status(wait=True, timeout=20)


async def test_async_restart(async_client):
    # Let it start up
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    await asyncio.sleep(0.2)

    # Kill the binary and wait for it to restart
    p = psutil.Process(async_client.binary._process.pid)
    p.kill()
    await asyncio.sleep(0.2)
    # assert client.binary._process.poll() is not None

    await api.status(wait=True, timeout=20)
