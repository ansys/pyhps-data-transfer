from ansys.hps.dt_client.data_transfer import AsyncDataTransferApi, DataTransferApi


def test_status(client):
    api_instance = DataTransferApi(client)
    resp = api_instance.status()
    assert resp.build_info is not None


async def test_async_status(async_client):
    api_instance = AsyncDataTransferApi(async_client)
    resp = await api_instance.status()
    assert resp.build_info is not None
