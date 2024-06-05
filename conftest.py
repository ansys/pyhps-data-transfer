import os

import pytest

from ansys.hps.dt_client.data_transfer.authenticate import authenticate


@pytest.fixture
def binary_path():
    return os.environ.get("BINARY_PATH", "./bin/hpsdata.exe")


@pytest.fixture(scope="session")
def access_token():
    tokens = authenticate(username="repadmin", password="repadmin", verify=False)
    return tokens.get("access_token", None)
