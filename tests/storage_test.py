from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi


def test_storage(client):
    api_instance = DataTransferApi(client)
    resp = api_instance.storages()
    assert len(resp) > 0


async def test_async_storage(async_client):
    api_instance = AsyncDataTransferApi(async_client)
    resp = await api_instance.storages()
    assert len(resp) > 0
