import time

from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState


def test_mkdir(client):
    api_instance = DataTransferApi(client)
    resp = api_instance.mkdir([StoragePath(path="test_mkdir")])
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(1)
        resp = api_instance.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            break


async def test_async_mkdir(async_client):
    api_instance = AsyncDataTransferApi(async_client)
    resp = await api_instance.mkdir([StoragePath(path="test_mkdir")])
    operation_id = resp.id
    assert operation_id is not None
    for _ in range(10):
        time.sleep(1)
        resp = await api_instance.operations([operation_id])
        if resp[0].state == OperationState.Succeeded:
            break
