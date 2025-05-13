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

===========================
Startup PyHPS Data Transfer
===========================

Example script to start data transfer service client and query available storage.

Example usage:
``python examples/data_transfer_runner.py --debug``
"""

import json
import logging
import time

import typer
from typing_extensions import Annotated

from ansys.hps.data_transfer.client import Client, DataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate


def main(
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
    url: Annotated[str, typer.Option(help="HPS URL to connect to")] = "https://localhost:8443/hps",
    username: Annotated[str, typer.Option(help="Username to authenticate with")] = "repadmin",
    password: Annotated[
        str, typer.Option(prompt=True, hide_input=True, help="Password to authenticate with")
    ] = "repadmin",
):

    auth_url = f"{url}/auth/realms/rep"
    log = logging.getLogger()
    logging.basicConfig(format="%(levelname)8s > %(message)s", level=logging.DEBUG)

    user_token = authenticate(username=username, password=password, verify=False, url=auth_url)
    user_token = user_token.get("access_token", None)
    assert user_token is not None

    client = Client()
    client.binary_config.update(
        verbosity=3,
        debug=debug,
        insecure=True,
        token=user_token,
    )

    client.binary_config.debug = True
    client.start()
    api = DataTransferApi(client)
    s = api.status(wait=True)
    log.info("Status: %s" % s)

    log.info("Available storage:")
    for d in api.storages():
        log.info(f"- {json.dumps(d, indent=4)}")

    for i in range(10):
        log.info("Idling for a while...")
        time.sleep(2)

    client.stop()


if __name__ == "__main__":
    typer.run(main)
