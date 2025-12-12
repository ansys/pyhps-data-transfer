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

"""This module contains tests for verifying the functionality and performance of
data transfer operations using multiprocessing and multithreading techniques
with the Data Transfer API and Async Data Transfer API from the Ansys HPS Data Transfer Client.
"""

import asyncio
import concurrent.futures
import logging
import multiprocessing as mp
import time

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi

log = logging.getLogger(__name__)


def _check_storage(dt_api, clt, bin):
    log.info(dt_api.storages())


def _async_check_storage(dt_api, clt, bin):
    s = asyncio.run(dt_api.storages())
    log.info(s)


def test_mp_support(client):
    """Test multiprocessing support."""
    api = DataTransferApi(client)
    api.status(wait=True)

    # Brute force wait for logging thread to start ... github was too slow ...
    while client.binary._log_thread is None:
        log.info("Waiting for logging thread to start...")
        time.sleep(1)
    time.sleep(5)

    p = mp.Process(target=_check_storage, args=(api, client, client.binary))
    p.start()
    p.join()

    pool = concurrent.futures.ProcessPoolExecutor()
    f = pool.submit(_check_storage, api)
    concurrent.futures.wait([f])


async def test_async_mp_support(async_client):
    """Test multiprocessing support using the async API."""
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    # Brute force wait for logging thread to start ... github was too slow ...
    while async_client.binary._log_thread is None:
        log.info("Waiting for logging thread to start...")
        asyncio.sleep(1)
    asyncio.sleep(5)

    p = mp.Process(target=_async_check_storage, args=(api, async_client, async_client.binary))
    p.start()
    p.join()

    pool = concurrent.futures.ProcessPoolExecutor()
    f = pool.submit(_async_check_storage, api)
    concurrent.futures.wait([f])
