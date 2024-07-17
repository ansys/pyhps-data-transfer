import asyncio

from keycloak import KeycloakAdmin
import pytest

from ansys.hps.dt_client.data_transfer.authenticate import authenticate
from ansys.hps.dt_client.data_transfer.binary import BinaryConfig

# @pytest.fixture(scope="session")
# def binary_path():
#     bin_ext = ".exe" if sys.platform == "win32" else ""
#     return os.environ.get("BINARY_PATH", os.path.join("bin", f"hpsdata{bin_ext}"))


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
def binary_config(admin_access_token, dt_url):
    cfg = BinaryConfig(
        data_transfer_url=dt_url,
        insecure=True,
        verbosity=3,
        debug=True,
        # path=binary_path,
        token=admin_access_token,
    )
    yield cfg


@pytest.fixture(scope="session")
def user_binary_config(user_access_token, dt_url):
    cfg = BinaryConfig(
        data_transfer_url=dt_url,
        insecure=True,
        verbosity=3,
        debug=True,
        # path=binary_path,
        token=user_access_token,
    )
    yield cfg


@pytest.fixture(scope="session")
def client(binary_config):
    from ansys.hps.dt_client.data_transfer import Client

    c = Client(bin_config=binary_config)
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
def user_client(user_binary_config):
    from ansys.hps.dt_client.data_transfer import Client

    c = Client(bin_config=user_binary_config)
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
async def async_client(binary_config, event_loop):
    from ansys.hps.dt_client.data_transfer import AsyncClient

    c = AsyncClient(bin_config=binary_config)
    await c.start()
    yield c
    await c.stop()


@pytest.fixture(scope="session")
async def async_user_client(user_binary_config, event_loop):
    from ansys.hps.dt_client.data_transfer import AsyncClient

    c = AsyncClient(bin_config=user_binary_config)
    await c.start()
    yield c
    await c.stop()
