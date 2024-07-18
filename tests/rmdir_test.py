from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState


def test_rmdir(storage_path, client):
    api = DataTransferApi(client)

    dst = StoragePath(path=f"{storage_path}/a/b")

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == False

    op = api.mkdir([dst])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == True

    op = api.rmdir([dst])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.exists([dst])
    op = api.wait_for(op.id)
    assert op[0].result == False


async def test_async_rmdir(storage_path, async_client):
    api = AsyncDataTransferApi(async_client)

    dst = StoragePath(path=f"{storage_path}/a/b")

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == False

    op = await api.mkdir([dst])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == True

    op = await api.rmdir([dst])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.exists([dst])
    op = await api.wait_for(op.id)
    assert op[0].result == False
