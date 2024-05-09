import os
import tempfile
import time

from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dtsc.api.dtsc_api import DtscApi
from ansys.rep.data.transfer.client.dtsc.models.ops import OperationState
from ansys.rep.data.transfer.client.dtsc.models.rest import SrcDst, StoragePath


def test_copy():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtscApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        temp_file_name = os.path.basename(temp_file.name)
        resp = api_instance.upload_file("any", temp_file_name, temp_file.name)
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = api_instance.copy([SrcDst(dst=StoragePath(path="test_copy"), src=StoragePath(path=temp_file_name))])
        assert resp.id is not None


async def test_async_copy():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
        sync=False,
    ) as async_api_client:
        api_instance = DtscApi(async_api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        temp_file_name = os.path.basename(temp_file.name)
        resp = await api_instance.async_upload_file("any", temp_file_name, temp_file.name)
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.async_operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = await api_instance.async_copy(
            [SrcDst(dst=StoragePath(path="test_copy"), src=StoragePath(path=temp_file_name))]
        )
        assert resp.id is not None
