import os
import tempfile
import time

from ansys.hps.dt_client.data_transfer import AsyncClient, AsyncDataTransferApi, Client, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState


def test_remove(binary_path, access_token):
    with Client(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url="http://localhost:1091",
        run_client_binary=True,
        binary_path=binary_path,
        token=access_token,
    ) as api_client:
        api_instance = DataTransferApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        resp = api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = api_instance.remove([StoragePath(path=os.path.basename(temp_file.name))])
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break


async def test_async_remove(binary_path, access_token):
    with AsyncClient(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url="http://localhost:1091",
        run_client_binary=True,
        binary_path=binary_path,
        token=access_token,
    ) as api_client:
        api_instance = AsyncDataTransferApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        resp = await api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = await api_instance.remove([StoragePath(path=os.path.basename(temp_file.name))])
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break
