import logging
import os
import tempfile

from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState

log = logging.getLogger(__name__)


def test_list(storage_path, client):
    api = DataTransferApi(client)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    names = ["file_1", "file_2"]

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = [StoragePath(path=f"{storage_path}/{name}") for name in names]
    op = api.copy([SrcDst(src=src, dst=dst) for dst in dsts])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = api.list([StoragePath(path=storage_path)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    result = next(iter(op[0].result.values()))
    assert names[0] in result
    assert names[1] in result


async def test_async_list(storage_path, async_client):
    api = AsyncDataTransferApi(async_client)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    names = ["file_1", "file_2"]

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = [StoragePath(path=f"{storage_path}/{name}") for name in names]
    op = await api.copy([SrcDst(src=src, dst=dst) for dst in dsts])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    op = await api.list([StoragePath(path=storage_path)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    result = next(iter(op[0].result.values()))
    assert names[0] in result
    assert names[1] in result
