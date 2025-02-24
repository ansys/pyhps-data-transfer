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

import json
import logging
import time

from ansys.hps.data_transfer.client import Client, DataTransferApi
from tests.utils import authenticate

log = logging.getLogger(__name__)

hps_url = "https://localhost:8443/hps"
dt_url = f"{hps_url}/dt/api/v1"
auth_url = f"{hps_url}/auth/realms/rep"

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(levelname)8s > %(message)s", level=logging.DEBUG)

    user_token = authenticate(username="repuser", password="repuser", verify=False, url=auth_url)
    user_token = user_token.get("access_token", None)
    assert user_token is not None

    client = Client()
    client.binary_config.update(
        verbosity=3,
        debug=False,
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
