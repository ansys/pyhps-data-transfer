from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi


def test_status(client):
    api = DataTransferApi(client)
    api.status(wait=True)
    resp = api.status()
    assert resp.build_info is not None


async def test_async_status(async_client):
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)
    resp = await api.status()
    assert resp.build_info is not None
