import os
import tempfile
import time

from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState


def test_list(client):
    api_instance = DataTransferApi(client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)
    resp = api_instance.upload_file("any", temp_file_name, temp_file.name)
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(1)
        resp = api_instance.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            break
    resp = api_instance.list([StoragePath(path="")])
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(1)
        resp = api_instance.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            break
    assert temp_file_name in resp[0].result["any:"]


async def test_async_list(async_client):
    api_instance = AsyncDataTransferApi(async_client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)
    resp = await api_instance.upload_file("any", temp_file_name, temp_file.name)
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(1)
        resp = await api_instance.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            break
    resp = await api_instance.list([StoragePath(path="")])
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(1)
        resp = await api_instance.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            break
    assert temp_file_name in resp[0].result["any:"]
