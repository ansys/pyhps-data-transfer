import asyncio
import os
import sys

from keycloak import KeycloakAdmin
import pytest

from ansys.hps.dt_client.data_transfer.authenticate import authenticate


@pytest.fixture(scope="session")
def binary_path():
    bin_ext = ".exe" if sys.platform == "win32" else ""
    return os.environ.get("BINARY_PATH", os.path.join("bin", f"hpsdata{bin_ext}"))


@pytest.fixture(scope="session")
def admin_access_token(auth_url):
    tokens = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    return tokens.get("access_token", None)


@pytest.fixture(scope="session")
def user_access_token(auth_url):
    tokens = authenticate(username="repuser", password="repuser", verify=False, url=auth_url)
    return tokens.get("access_token", None)


@pytest.fixture(scope="session")
def dt_url():
    return "https://localhost:8443/hps/dt/api/v1"


@pytest.fixture(scope="session")
def keycloak_url():
    return "https://localhost:8443/hps/auth"


@pytest.fixture(scope="session")
def auth_url(keycloak_url):
    return f"{keycloak_url}/realms/rep"


@pytest.fixture(scope="session")
def keycloak_client(keycloak_url):
    admin = KeycloakAdmin(
        server_url=keycloak_url + "/",
        username="keycloak",
        password="keycloak123",
        realm_name="rep",
        user_realm_name="master",
        verify=False,
    )
    yield admin


@pytest.fixture(scope="session")
def user_id(keycloak_client):
    user_id = keycloak_client.get_user_id("repuser")
    return user_id


@pytest.fixture(scope="session")
def event_loop():
    # https://stackoverflow.com/a/71668965
    loop = asyncio.get_event_loop()

    yield loop

    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(1))

    loop.close()


@pytest.fixture(scope="session")
def client(binary_path, admin_access_token, dt_url):
    from ansys.hps.dt_client.data_transfer import Client

    c = Client(
        data_transfer_url=dt_url,
        run_client_binary=True,
        binary_path=binary_path,
        token=admin_access_token,
        port=2000,
    )
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
def user_client(binary_path, user_access_token, dt_url):
    from ansys.hps.dt_client.data_transfer import Client

    c = Client(
        data_transfer_url=dt_url,
        run_client_binary=True,
        binary_path=binary_path,
        token=user_access_token,
        port=2001,
    )
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
def async_client(binary_path, admin_access_token, dt_url, event_loop):
    from ansys.hps.dt_client.data_transfer import AsyncClient

    c = AsyncClient(
        data_transfer_url=dt_url,
        run_client_binary=True,
        binary_path=binary_path,
        token=admin_access_token,
        port=2002,
    )
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
def async_user_client(binary_path, user_access_token, dt_url, event_loop):
    from ansys.hps.dt_client.data_transfer import AsyncClient

    c = AsyncClient(
        data_transfer_url=dt_url,
        run_client_binary=True,
        binary_path=binary_path,
        token=user_access_token,
        port=2003,
    )
    c.start()
    yield c
    c.stop()
