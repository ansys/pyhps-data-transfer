import os
import tempfile
import time

from ansys.rep.data.transfer.client.api import DataTransferApi
from ansys.rep.data.transfer.client.api.async_api import AsyncDataTransferApi
from ansys.rep.data.transfer.client.client import AsyncClient, Client
from ansys.rep.data.transfer.client.models.ops import OperationState
from ansys.rep.data.transfer.client.models.rest import StoragePath


def test_remove(binary_path):
    with Client(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = DataTransferApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        resp = api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = api_instance.remove([StoragePath(path=os.path.basename(temp_file.name))])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break


async def test_async_remove(binary_path):
    with AsyncClient(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = AsyncDataTransferApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        resp = await api_instance.async_upload_file("any", os.path.basename(temp_file.name), temp_file.name)
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.async_operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = await api_instance.async_remove([StoragePath(path=os.path.basename(temp_file.name))])
        assert resp.id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.async_operations([resp.id])
            if resp[0].state == OperationState.Succeeded:
                break
