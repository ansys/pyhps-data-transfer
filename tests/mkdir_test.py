import time
from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dts.api.dts_api import DtsApi
from openapi_client.models.rest_storage_path import RestStoragePath
from openapi_client.models.ops_operation_state import OpsOperationState

def test_mkdir():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True
    ) as api_client:
        api_instance = DtsApi(api_client)
        resp = api_instance.mkdir([RestStoragePath(path='test_mkdir')])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp.operations[0].state == OpsOperationState.SUCCEEDED:
                break
