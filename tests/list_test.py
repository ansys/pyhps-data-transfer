import os
import tempfile
import time

from openapi_client.models.ops_operation_state import OpsOperationState
from openapi_client.models.rest_storage_path import RestStoragePath

from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dts.api.dts_api import DtsApi


def test_list():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtsApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        temp_file_name = os.path.basename(temp_file.name)
        resp = api_instance.upload_file("any", temp_file_name, temp_file.name)
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp.operations[0].state == OpsOperationState.SUCCEEDED:
                break
        resp = api_instance.list([RestStoragePath(path="")])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp.operations[0].state == OpsOperationState.SUCCEEDED:
                break
        assert temp_file_name in resp.operations[0].result["any:"]
