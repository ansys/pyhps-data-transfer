from ansys.hps.dt_client.data_transfer import AsyncClient, Client, AsyncDataTransferApi, DataTransferApi


def test_storage(binary_path):
    with Client(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = DataTransferApi(api_client)
        resp = api_instance.storages()
        assert len(resp) > 0


async def test_async_storage(binary_path):
    with AsyncClient(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = AsyncDataTransferApi(api_client)
        resp = await api_instance.storages()
        assert len(resp) > 0
