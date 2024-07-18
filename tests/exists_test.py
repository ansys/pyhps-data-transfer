import os
import tempfile

from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState


def test_exists(test_name, client):
    api = DataTransferApi(client)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{temp_file_name}")

    op = api.exists([dst])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert op[0].result == False

    op = api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.exists([dst])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert op[0].result == True


async def test_async_exists(test_name, async_client):
    api = AsyncDataTransferApi(async_client)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{temp_file_name}")

    op = await api.exists([dst])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert op[0].result == False

    op = await api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.exists([dst])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert op[0].result == True
