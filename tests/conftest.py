# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import logging
import os
import shutil
import traceback

import backoff
from keycloak import KeycloakAdmin
import pytest
from slugify import slugify

from ansys.hps.data_transfer.client import AsyncClient, Client, DataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate
from ansys.hps.data_transfer.client.binary import BinaryConfig
from ansys.hps.data_transfer.client.models.msg import StoragePath

log = logging.getLogger(__name__)

# @pytest.fixture(scope="session")
# def binary_path():
#     bin_ext = ".exe" if sys.platform == "win32" else ""
#     return os.environ.get("BINARY_PATH", os.path.join("bin", f"hpsdata{bin_ext}"))


def _backoff_handler(details, title, exc_info=True):
    try:
        title = f"{title[0].upper()}{title[1:]}"
        msg = "{title}, backing off {wait:0.1f} seconds after {tries} tries: {exception}".format(title=title, **details)
        log.info(msg)
        if exc_info:
            try:
                ex_str = "\n".join(traceback.format_exception(details["exception"]))
                log.debug(f"Backoff caused by:\n{ex_str}")
            except:
                pass
    except Exception as ex:
        log.warning(f"Failed to log in backoff handler: {ex}")


def _success_handler(details, title):
    try:
        title = f"{title[0].upper()}{title[1:]}"
        log.debug("{title}, succeeded after {tries} tries".format(title=title, **details))
    except Exception as ex:
        log.warning(f"Failed to log in success handler: {ex}")


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
@backoff.on_exception(
    backoff.expo,
    Exception,
    max_time=120,
    # max_tries=20,
    jitter=backoff.full_jitter,
    raise_on_giveup=True,
    on_backoff=lambda details: _backoff_handler(details, "getting admin access token"),
    on_success=lambda details: _success_handler(details, "getting admin access token"),
    logger=__name__,
)
def admin_access_token(auth_url):
    tokens = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    return tokens.get("access_token", None)


@pytest.fixture(scope="session")
@backoff.on_exception(
    backoff.expo,
    Exception,
    max_time=120,
    # max_tries=20,
    jitter=backoff.full_jitter,
    raise_on_giveup=True,
    on_backoff=lambda details: _backoff_handler(details, "getting user access token"),
    on_success=lambda details: _success_handler(details, "getting user access token"),
    logger=__name__,
)
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


@pytest.fixture
def client(binary_config, binary_dir):
    from ansys.hps.data_transfer.client import Client

    c = Client(bin_config=binary_config, download_dir=binary_dir, clean_dev=False)
    c.start()
    yield c

    c.stop()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_storages(binary_config, binary_dir):
    yield

    c = Client(bin_config=binary_config, download_dir=binary_dir, clean_dev=False)
    c.start()
    api = DataTransferApi(c)
    op = api.rmdir([StoragePath(path="python_client_tests")])
    api.wait_for(op.id)


@pytest.fixture
def user_client(user_binary_config, binary_dir):
    c = Client(bin_config=user_binary_config, download_dir=binary_dir, clean_dev=False)
    c.start()
    yield c
    c.stop()


@pytest.fixture
async def async_client(binary_config, binary_dir, event_loop):
    c = AsyncClient(bin_config=binary_config, download_dir=binary_dir, clean_dev=False)
    await c.start()
    yield c

    await c.stop()


@pytest.fixture
async def async_user_client(user_binary_config, binary_dir, event_loop):
    c = AsyncClient(bin_config=user_binary_config, download_dir=binary_dir, clean_dev=False)
    await c.start()
    yield c
    await c.stop()

@pytest.fixture
def build_info_path():
    return os.path.join(os.getcwd(), "build_info.json")
