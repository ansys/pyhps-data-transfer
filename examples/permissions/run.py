# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

import glob
import logging
import os
import pathlib
import traceback

from keycloak import KeycloakAdmin

from ansys.hps.data_transfer.client import Client, DataTransferApi
from tests.utils import authenticate
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.permissions import (
    Resource,
    ResourceType,
    RoleAssignment,
    RoleQuery,
    RoleType,
    Subject,
    SubjectType,
)

stream_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s", datefmt="%H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.DEBUG)
log = logging.getLogger("ansys.hps")
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)


hps_url = "https://localhost:8443/hps"
keycloak_url = f"{hps_url}/auth"
auth_url = f"{keycloak_url}/realms/rep"
dt_url = f"{hps_url}/dt/api/v1"


def get_user_id_from_keycloak():
    admin = KeycloakAdmin(
        server_url=keycloak_url + "/",
        username="keycloak",
        password="keycloak123",
        realm_name="rep",
        user_realm_name="master",
        verify=False,
    )
    user_id = admin.get_user_id("repuser")
    return user_id


if __name__ == "__main__":
    run_bin = True

    log.info("### Logging in as repuser ...")
    user_token = authenticate(username="repuser", password="repuser", verify=False, url=auth_url)
    user_token = user_token.get("access_token", None)
    assert user_token is not None

    log.info("### Preparing data transfer client for 'repuser' ...")
    user_client = Client()
    user_client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=user_token,
        data_transfer_url=dt_url,
    )
    user_client.start()

    user = DataTransferApi(user_client)
    user.status(wait=True)

    log.info("### Checking binary's status ...")
    status = user.status(wait=True)
    log.info(f"### Client binary status: {status}")

    source_dir = pathlib.Path(__file__).parent / "files"
    source_dir = os.path.relpath(source_dir, os.getcwd())
    log.info(f"### Searching for files to copy in {source_dir} ...")
    files = glob.glob(os.path.join(source_dir, "**", "*.*"), recursive=True)
    log.info("Found files:")
    for file in files:
        log.info(f"- {file}")

    log.info("### Trying to copy files as 'repuser'...")
    target_dir = "permissions_demo"
    src_dst = [
        SrcDst(
            src=StoragePath(path=f, remote="local"),
            dst=StoragePath(
                path=os.path.normpath(
                    os.path.join(target_dir, os.path.relpath(os.path.dirname(f), source_dir), os.path.basename(f))
                ),
                remote="any",
            ),
        )
        for f in files
    ]
    log.info("### Operations to be executed: ")
    for sd in src_dst:
        log.info(f"- {sd.src.remote}:{sd.src.path} -> {sd.dst.remote}:{sd.dst.path}")

    try:
        # The operation will fail because 'repuser' does not have the necessary permissions
        resp = user.copy(src_dst)
    except Exception as ex:
        log.error(f"Encountered error: {ex}")

    admin_token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    admin_token = admin_token.get("access_token", None)

    log.info("### Preparing data transfer client for 'repadmin' ...")
    admin_client = Client()
    admin_client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=admin_token,
        data_transfer_url=dt_url,
    )
    admin_client.start()

    admin = DataTransferApi(admin_client)
    admin.status(wait=True)

    log.info("### Granting 'repuser' the necessary permissions ...")
    user_id = get_user_id_from_keycloak()

    try:
        admin.set_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )
    except Exception as ex:
        log.info(ex)

    try:
        log.info("### Verifying permissions for 'repuser' ...")
        resp = admin.check_permissions(
            [
                RoleQuery(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )

        log.info(f"### Is 'repuser'({user_id}) allowed to read from {target_dir}? -> {resp.allowed}")

        log.info("### Trying to copy files as 'repuser' one more time...")
        resp = user.copy(src_dst)
        op = user.wait_for([resp.id], timeout=None)[0]
        log.info(f"### Copy operation state: {op.state}")

        log.info("### Listing files in the target directory as 'repadmin' ...")
        resp = admin.list([StoragePath(path=target_dir, remote="any")])
        op = admin.wait_for([resp.id], timeout=10)[0]
        log.info(f"### Result: {op.result}")

        target_dir = os.path.join(os.path.dirname(__file__), "downloaded")
        log.info(f"### Downloading files to {target_dir}...")
        src_dst = [
            SrcDst(
                src=sd.dst,
                dst=StoragePath(remote="local", path=os.path.join(target_dir, os.path.basename(sd.dst.path))),
            )
            for sd in src_dst
        ]
        resp = admin.copy(src_dst)
        op = admin.wait_for([resp.id], timeout=300)[0]
        log.info(f"### Copy operation state: {op.state}")
    except Exception as ex:
        log.debug(traceback.format_exc())
        log.error(f"Error: {ex}")
    finally:
        log.info("Removing permissions for 'repuser' ...")
        admin.remove_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role="writer",
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )

    log.info("And that's all folks!")

    admin_client.stop()
    user_client.stop()
