from ansys.hps.data_transfer_client import __version__


def test_pkg_version():
    import importlib.metadata as importlib_metadata

    # Read from the pyproject.toml
    # major, minor, patch
    read_version = importlib_metadata.version("ansys-hps-data-transfer-client")

    assert __version__ == read_version
