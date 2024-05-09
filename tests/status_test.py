from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dtsc.api.dtsc_api import DtscApi


def test_status():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtscApi(api_client)
        resp = api_instance.status()
        assert resp.build_info is not None


async def test_async_status():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
        sync=False,
    ) as api_client:
        api_instance = DtscApi(api_client)
        resp = await api_instance.async_status()
        assert resp.build_info is not None
