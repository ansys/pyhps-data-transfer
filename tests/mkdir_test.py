import time

from ansys.rep.data.transfer.client.client import Client, AsyncClient
from ansys.rep.data.transfer.client.api import DataTransferApi
from ansys.rep.data.transfer.client.api.async_api import AsyncDataTransferApi
from ansys.rep.data.transfer.client.models.ops import OperationState
from ansys.rep.data.transfer.client.models.rest import StoragePath


def test_mkdir():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DataTransferApi(api_client)
        resp = api_instance.mkdir([StoragePath(path="test_mkdir")])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break


async def test_async_mkdir():
    with AsyncClient(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
    ) as api_client:
        api_instance = AsyncDataTransferApi(api_client)
        resp = await api_instance.async_mkdir([StoragePath(path="test_mkdir")])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.async_operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
