import asyncio
import os
import shutil

from keycloak import KeycloakAdmin
import pytest
from slugify import slugify

from ansys.hps.dt_client.data_transfer.authenticate import authenticate
from ansys.hps.dt_client.data_transfer.binary import BinaryConfig

# @pytest.fixture(scope="session")
# def binary_path():
#     bin_ext = ".exe" if sys.platform == "win32" else ""
#     return os.environ.get("BINARY_PATH", os.path.join("bin", f"hpsdata{bin_ext}"))


@pytest.fixture()
def test_name(request):
    return slugify(request.node.name)


@pytest.fixture(scope="session")
def binary_dir():
    return os.path.join(os.getcwd(), "test_run", "bin")


@pytest.fixture()
def storage_path(test_name):
    return f"python_client_tests/{test_name}"


@pytest.fixture(autouse=True)
def for_every_test(request, test_name):
    module_name = request.node.module.__name__.replace(".", "_")

    test_run_directory = os.path.join(os.getcwd(), "test_run")
    test_directory = os.path.join(test_run_directory, module_name, test_name)

    if os.path.isdir(test_directory):
        shutil.rmtree(test_directory)
    os.makedirs(test_directory)

    old_cwd = os.getcwd()
    os.chdir(test_directory)

    yield

    os.chdir(old_cwd)


@pytest.fixture(scope="session", autouse=True)
def remove_binaries(binary_dir):
    if os.path.isdir(binary_dir):
        shutil.rmtree(binary_dir)


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
def client(binary_config, binary_dir):
    from ansys.hps.dt_client.data_transfer import Client

    c = Client(bin_config=binary_config, download_dir=binary_dir)
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
def user_client(user_binary_config, binary_dir):
    from ansys.hps.dt_client.data_transfer import Client

    c = Client(bin_config=user_binary_config, download_dir=binary_dir)
    c.start()
    yield c
    c.stop()


@pytest.fixture(scope="session")
async def async_client(binary_config, binary_dir, event_loop):
    from ansys.hps.dt_client.data_transfer import AsyncClient

    c = AsyncClient(bin_config=binary_config, download_dir=binary_dir)
    await c.start()
    yield c

    await c.stop()


@pytest.fixture(scope="session")
async def async_user_client(user_binary_config, binary_dir, event_loop):
    from ansys.hps.dt_client.data_transfer import AsyncClient

    c = AsyncClient(bin_config=user_binary_config, download_dir=binary_dir)
    await c.start()
    yield c
    await c.stop()
