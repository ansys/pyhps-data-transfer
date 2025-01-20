import logging
import os
import tempfile
import time
import pytest

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.ops import OperationState

log = logging.getLogger(__name__)

num_files = 2
file_size = 5  # GB


def write_file(file_name, size):
    start_time = time.time()
    log.info(f"Generating file {file_name} with size {size} GB")
    gb1 = 1024 * 1024 * 1024  # 1GB
    with open(file_name, "wb") as fout:
        for i in range(size):
            fout.write(os.urandom(gb1))
    log.info(f"File {file_name} has been generated after {(time.time() - start_time):.2f} seconds")
    return 0


#TODO:remove skip
@pytest.mark.skip(reason="TODO: test fails")
def test_large_batch(storage_path, client):
    api = DataTransferApi(client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        write_file(temp_file.name, file_size)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []
    for i in range(num_files):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    log.info("Starting copy ...")
    op = api.copy(dsts)
    assert op.id is not None
    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages


#TODO:remove skip
@pytest.mark.skip(reason="TODO: test fails")
async def test_async_large_batch(storage_path, async_client):
    api = AsyncDataTransferApi(async_client)
    api.status(wait=True)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        write_file(temp_file.name, file_size)
    temp_file_name = os.path.basename(temp_file.name)

    src = StoragePath(path=temp_file.name, remote="local")
    dsts = []
    for i in range(num_files):
        dst = StoragePath(path=f"{storage_path}/{temp_file_name}_{i}")
        dsts.append(SrcDst(src=src, dst=dst))

    log.info("Starting copy ...")
    op = await api.copy(dsts)
    assert op.id is not None
    op = await api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages
