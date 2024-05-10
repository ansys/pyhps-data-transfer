import os
import tempfile
import time

from ansys.rep.data.transfer.client.api.api import DataTransferApi
from ansys.rep.data.transfer.client.api.async_api import AsyncDataTransferApi
from ansys.rep.data.transfer.client.client import AsyncClient, Client
from ansys.rep.data.transfer.client.models.ops import OperationState
from ansys.rep.data.transfer.client.models.rest import SrcDst, StoragePath


def test_copy(binary_path):
    with Client(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = DataTransferApi(api_client)
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


async def test_async_copy(binary_path):
    with AsyncClient(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as async_api_client:
        api_instance = AsyncDataTransferApi(async_api_client)
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
