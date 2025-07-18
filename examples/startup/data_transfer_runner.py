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
.. _ref_runner:

=========================
Start PyHPS Data Transfer
=========================

This example script starts a data transfer service client and queries available storage.

Example usage:
``python examples/data_transfer_runner.py --debug``
"""

import json
import logging
import time
import jwt

import typer
from typing_extensions import Annotated

from ansys.hps.data_transfer.client import Client, DataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate


def main(
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
    url: Annotated[str, typer.Option(help="HPS URL to connect to")] = "https://localhost:8443/hps",
    username: Annotated[str, typer.Option(help="Username to authenticate with")] = "repadmin",
    password: Annotated[str, typer.Option(help="Password to authenticate with")] = "repadmin",
):

    auth_url = f"{url}/auth/realms/rep"
    log = logging.getLogger()
    logging.basicConfig(format="%(levelname)8s > %(message)s", level=logging.DEBUG)

    def refresh_token():
        user_token = authenticate(username=username, password=password, verify=False, url=auth_url)
        user_token = user_token.get("access_token", None)
        return user_token
    
    # Call refresh_token() once to get the access token
    user_token = refresh_token()
    assert user_token is not None

    decoded_token = jwt.decode(user_token, options={"verify_signature": False})    
    exp_time = decoded_token.get("exp", None)
    if exp_time:
        log.info(f"Token expiration time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp_time))}")

    client = Client(refresh_token_callback=refresh_token)
    client.binary_config.update(
        verbosity=3,
        debug=debug,
        insecure=True,
        token=user_token,
        auth_type="oidc", # Use OIDC for authentication
    )

    client.binary_config.debug = True
    client.start()
    api = DataTransferApi(client)
    s = api.status(wait=True)
    log.info("Status: %s" % s)

    log.info("Available storage:")
    for _ in range(5):
        for d in api.storages():
            log.info(f"- {json.dumps(d, indent=4)}")
        log.info("+++====== Idling for a while...")
        time.sleep(10)

    client.stop()


if __name__ == "__main__":
    typer.run(main)
