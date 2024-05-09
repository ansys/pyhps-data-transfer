from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dtsc.api.dtsc_api import DtscApi


def test_storage():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtscApi(api_client)
        resp = api_instance.storages()
        assert len(resp) > 0


async def test_async_storage():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
        sync=False,
    ) as api_client:
        api_instance = DtscApi(api_client)
        resp = await api_instance.async_storages()
        assert len(resp) > 0
