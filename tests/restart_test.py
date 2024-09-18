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
