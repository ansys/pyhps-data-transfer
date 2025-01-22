import logging
import time

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate

log = logging.getLogger(__name__)


def test_token_passing(client, admin_token, auth_url):
    api = DataTransferApi(client)
    api.status(wait=True)

    expires_in = admin_token["expires_in"]
    log.info(f"Token expires in {expires_in} seconds")

    s = api.status()
    assert s.ready

    tk = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    client.binary_config.token = tk["access_token"]
    assert client.binary_config.token == tk["access_token"]

    time.sleep(2)

    s = api.status()
    assert s.ready


async def test_async_token_passing(async_client, admin_token, auth_url):
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
