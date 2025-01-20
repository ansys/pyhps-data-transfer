import logging
import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

log = logging.getLogger(__name__)

num_copies = 200
content = "Mock file; " * 100

#TODO:remove skip
def test_large_batch(storage_path, client):
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(content)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []

    for i in range(num_copies):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    op = api.copy(dsts)
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages


async def test_async_large_batch(storage_path, async_client):
    api = AsyncDataTransferApi(async_client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(content)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []

    for i in range(num_copies):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    op = await api.copy(dsts)
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
