import logging
import os
import tempfile

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

log = logging.getLogger(__name__)


def test_get_basic_metadata(storage_path, client):
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

    op = api.get_metadata([dst])
    op = api.wait_for(op.id)[0]
    assert op.state == OperationState.Succeeded, op.messages
    md = op.result[dst.path]
    assert md is not None
    assert md["size"] == os.path.getsize(temp_file.name)
    assert md["checksum"] != ""
    assert md["checksum"] == "ac2390bba2edaa01"


async def test_async_get_basic_metadata(storage_path, async_client):
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

    op = await api.get_metadata([dst])
    op = await api.wait_for(op.id)
    op = op[0]
    assert op.state == OperationState.Succeeded, op.messages
    md = op.result[dst.path]
    assert md is not None
    assert md["size"] == os.path.getsize(temp_file.name)
    assert md["checksum"] != ""
    assert md["checksum"] == "ac2390bba2edaa01"
