import filecmp
import logging
import os
import tempfile

from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi
from ansys.hps.dt_client.data_transfer.models.msg import SrcDst, StoragePath
from ansys.hps.dt_client.data_transfer.models.ops import OperationState

log = logging.getLogger(__name__)


def test_copy(storage_path, client):
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{storage_path}/{temp_file_name}")
    op = api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    src = dst
    dst = StoragePath(path=os.path.join(os.getcwd(), "downloaded.txt"), remote="local")
    op = api.copy([SrcDst(src=src, dst=dst)])
    op = api.wait_for([op])
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert filecmp.cmp(temp_file.name, dst.path, shallow=False)


async def test_async_copy(storage_path, async_client):
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dst = StoragePath(path=f"{storage_path}/{temp_file_name}")
    op = await api.copy([SrcDst(src=src, dst=dst)])
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    src = dst
    dst = StoragePath(path=os.path.join(os.getcwd(), "downloaded.txt"), remote="local")
    op = await api.copy([SrcDst(src=src, dst=dst)])
    op = await api.wait_for([op])
    assert op[0].state == OperationState.Succeeded, op[0].messages
    assert filecmp.cmp(temp_file.name, dst.path, shallow=False)
