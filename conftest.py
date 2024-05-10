import os

import pytest


@pytest.fixture(scope="session")
def some_fixture():
    pass


@pytest.fixture
def binary_path():
    return os.environ.get("BINARY_PATH", "./bin/hpsdata.exe")
