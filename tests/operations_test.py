import os
import tempfile

from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi


def test_operations(client):
    api_instance = DataTransferApi(client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    resp = api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
    resp = api_instance.operations([resp.id])
    assert len(resp) > 0


async def test_async_operations(async_client):
    api_instance = AsyncDataTransferApi(async_client)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Mock file")
    resp = await api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
    resp = await api_instance.operations([resp.id])
    assert len(resp) > 0
