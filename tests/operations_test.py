import os
import tempfile

from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dtsc.api.dtsc_api import DtscApi


def test_operations():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1", dtsc_url="http://localhost:1090", run_client_binary=True
    ) as api_client:
        api_instance = DtscApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        resp = api_instance.upload_file("any", os.path.basename(temp_file.name), temp_file.name)
        resp = api_instance.operations([resp.id])
        assert len(resp) > 0


async def test_async_operations():
    with Client(
        dts_url="https://localhost:8443/hps/dts/api/v1",
        dtsc_url="http://localhost:1090",
        run_client_binary=True,
        sync=False,
    ) as api_client:
        api_instance = DtscApi(api_client)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Mock file")
        resp = await api_instance.async_upload_file("any", os.path.basename(temp_file.name), temp_file.name)
        resp = await api_instance.async_operations([resp.id])
        assert len(resp) > 0
