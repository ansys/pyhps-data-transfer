import time

from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dts.api.dts_api import DtsApi
from ansys.rep.data.transfer.client.dts.models.ops import OperationState
from ansys.rep.data.transfer.client.dts.models.rest import SrcDst, StoragePath


def test_mkdir():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtsApi(api_client)
        resp = api_instance.mkdir([StoragePath(path="test_mkdir")])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = api_instance.move(
            [SrcDst(src=StoragePath(path="test_mkdir"), dst=StoragePath(path="nested/test_mkdir"))]
        )
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
