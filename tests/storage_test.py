from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi


def test_storage(client):
    api = DataTransferApi(client)
    api.status(wait=True)
    resp = api.storages()
    assert len(resp) > 0


async def test_async_storage(async_client):
    api = AsyncDataTransferApi(async_client)
    await api.status(wait=True)
    resp = await api.storages()
    assert len(resp) > 0
