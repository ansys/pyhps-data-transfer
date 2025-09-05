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

"""
.. _ref_permissions:

=========================
Set and query permissions
=========================

This example script sets and queries permissions on files and
directories using the data transfer service.

Example usage:
``python examples/set_permissions_example.py --local-path=examples/basic/files/hello``
"""

import glob
import logging
import os
import pathlib
import traceback

from keycloak import KeycloakAdmin
import typer
from typing_extensions import Annotated

from ansys.hps.data_transfer.client import Client, DataTransferApi, get_log_level
from ansys.hps.data_transfer.client.authenticate import authenticate
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath
from ansys.hps.data_transfer.client.models.permissions import (
    Resource,
    ResourceType,
    RoleAssignment,
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

######################################################################
# Define a method to get the user ID of ``repuser``` from Keycloak
# ================================================================
def get_user_id_from_keycloak(keycloak_url):
    """Get the user id of 'repuser' from Keycloak."""
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


##################################################################################
# Define a method to set and query permissions on files and directories
# =====================================================================
def permissions(api: DataTransferApi, url: str):
    """Set and query permissions on files and directories."""
    keycloak_url = f"{url}/auth"
    auth_url = f"{keycloak_url}/realms/rep"
    dt_url = f"{url}/dt/api/v1"

    log.info("### Checking binary's status ...")
    status = api.status(wait=True)
    log.info(f"### Client binary status: {status}")

    source_dir = pathlib.Path(__file__).parent / "files"
    source_dir = os.path.relpath(source_dir, os.getcwd())
    log.info(f"### Searching for files to copy in {source_dir} ...")
    files = glob.glob(os.path.join(source_dir, "**", "*.*"), recursive=True)
    log.info("Found files:")
    for file in files:
        log.info(f"- {file}")

##############################################################
# Copy files as ``repuser``
# =======================
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
    log.info("### Operations to execute: ")
    for sd in src_dst:
        log.info(f"- {sd.src.remote}:{sd.src.path} -> {sd.dst.remote}:{sd.dst.path}")

    try:
        # The operation fails because 'repuser' does not have the necessary permissions
        resp = api.copy(src_dst)
    except Exception as ex:
        log.error(f"Encountered error: {ex}")

    admin_token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    admin_token = admin_token.get("access_token", None)

##############################################################
# Create a data transfer client for ``repadmin``
# ==============================================
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

##############################################################
# Grant ``repuser`` the necessary permissions
# ===========================================
    log.info("### Granting 'repuser' the necessary permissions ...")
    user_id = get_user_id_from_keycloak(keycloak_url)

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

##############################################################
# Verify permissions for ``repuser``
# ==================================
    try:
        log.info("### Verifying permissions for 'repuser' ...")
        resp = admin.check_permissions(
            [
                RoleAssignment(
                    resource=Resource(path=target_dir, type=ResourceType.Doc),
                    role=RoleType.Writer,
                    subject=Subject(id=user_id, type=SubjectType.User),
                )
            ]
        )

        log.info(f"### Is 'repuser'({user_id}) allowed to read from {target_dir}? -> {resp.allowed}")

        log.info("### Trying to copy files as 'repuser' one more time...")
        resp = api.copy(src_dst)
        op = api.wait_for([resp.id], timeout=None)[0]
        log.info(f"### Copy operation state: {op.state}")

##############################################################
# List files in the target directory as ``repadmin``
# ==================================================
        log.info("### Listing files in the target directory as 'repadmin' ...")
        resp = admin.list([StoragePath(path=target_dir, remote="any")])
        op = admin.wait_for([resp.id], timeout=10)[0]
        log.info(f"### Result: {op.result}")

##############################################################
# Download files to ``downloaded`` directory
# ==========================================
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

    admin_client.stop()

###################################################
# Define the main function
# ========================
def main(
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
    verbosity: Annotated[int, typer.Option(help="Increase verbosity")] = 1,
    url: Annotated[str, typer.Option(help="HPS URL to connect to")] = "https://localhost:8443/hps",
    username: Annotated[str, typer.Option(help="Username to authenticate with")] = "repadmin",
    password: Annotated[
        str, typer.Option(prompt=True, hide_input=True, help="Password to authenticate with")
    ] = "repadmin",
):
    logging.basicConfig(format="%(levelname)8s > %(message)s", level=get_log_level(verbosity, debug))

    dt_url = f"{url}/dt/api/v1"
    auth_url = f"{url}/auth/realms/rep"

    token = authenticate(username=username, password=password, verify=False, url=auth_url)
    token = token.get("access_token", None)
    assert token is not None

    log.info("Connecting to the data transfer service client..")
    client = Client(clean=True)

    client.binary_config.update(
        verbosity=verbosity,
        debug=debug,
        insecure=True,
        token=token,
        data_transfer_url=dt_url,
    )
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)
    storage_names = [f"{s['name']}({s['type']})" for s in api.storages()]
    log.info(f"Available storages: {storage_names}")

    permissions(api=api, url=url)

    client.stop()


if __name__ == "__main__":
    typer.run(main)
