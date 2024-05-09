import time

from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dtsc.api.dtsc_api import DtscApi
from ansys.rep.data.transfer.client.dtsc.models.ops import OperationState
from ansys.rep.data.transfer.client.dtsc.models.rest import StoragePath


def test_mkdir():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtscApi(api_client)
        resp = api_instance.mkdir([StoragePath(path="test_mkdir")])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break


async def test_async_mkdir():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
        sync=False,
    ) as api_client:
        api_instance = DtscApi(api_client)
        resp = await api_instance.async_mkdir([StoragePath(path="test_mkdir")])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.async_operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
