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

import pytest

log = logging.getLogger(__name__)


@pytest.mark.order(1)
def test_services(client, build_info_path, dt_url):
    # make sure services are up and running, print info

    # check dts api
    r = client.session.get(dt_url)
    dt_info = r.json()
    log.info(f"Dt api info\n{json.dumps(dt_info, indent=2)}")
    assert "build_info" in dt_info

    info = {"dt": dt_info}
    with open(build_info_path, "w") as f:
        f.write(json.dumps(info, indent=2))

    with open(build_info_path.replace(".json", ".md"), "w") as f:
        f.write("### Build info")
        f.write("\n```json\n")
        f.write(json.dumps(info, indent=2))
        f.write("\n```")
