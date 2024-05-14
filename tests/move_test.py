import time

from ansys.hps.dt_client.data_transfer.api import DataTransferApi
from ansys.hps.dt_client.data_transfer.api.async_api import AsyncDataTransferApi
from ansys.hps.dt_client.data_transfer.client import AsyncClient, Client
from ansys.hps.dt_client.data_transfer.models.ops import OperationState
from ansys.hps.dt_client.data_transfer.models.rest import SrcDst, StoragePath


def test_mkdir(binary_path):
    with Client(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = DataTransferApi(api_client)
        resp = api_instance.mkdir([StoragePath(path="test_mkdir")])
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = api_instance.move(
            [SrcDst(src=StoragePath(path="test_mkdir"), dst=StoragePath(path="nested/test_mkdir"))]
        )
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break


async def test_async_mkdir(binary_path):
    with AsyncClient(
        data_transfer_url="https://localhost:8443/hps/dts/api/v1",
        external_url=None,
        run_client_binary=True,
        binary_path=binary_path,
    ) as api_client:
        api_instance = AsyncDataTransferApi(api_client)
        resp = await api_instance.mkdir([StoragePath(path="test_mkdir")])
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break
        resp = await api_instance.move(
            [SrcDst(src=StoragePath(path="test_mkdir"), dst=StoragePath(path="nested/test_mkdir"))]
        )
        operation_id = resp.id
        assert operation_id is not None
        for _ in range(10):
            time.sleep(1)
            resp = await api_instance.operations([operation_id])
            if resp[0].state == OperationState.Succeeded:
                break
