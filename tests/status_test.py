from ansys.rep.data.transfer.client.client import Client, AsyncClient
from ansys.rep.data.transfer.client.api import DataTransferApi
from ansys.rep.data.transfer.client.api.async_api import AsyncDataTransferApi


def test_status():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DataTransferApi(api_client)
        resp = api_instance.status()
        assert resp.build_info is not None


async def test_async_status():
    with AsyncClient(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
    ) as api_client:
        api_instance = AsyncDataTransferApi(api_client)
        resp = await api_instance.async_status()
        assert resp.build_info is not None
