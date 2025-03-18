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

"""Module contains tests for verifying the retry mechanism in the Data Transfer API
from the Ansys HPS Data Transfer Client.
"""

import logging

import httpx

from ansys.hps.data_transfer.client.api.retry import retry
from ansys.hps.data_transfer.client.exceptions import HPSError, NotReadyError, TimeoutError, raise_for_status

log = logging.getLogger(__name__)


class Counter:
    """Simple counter class."""

    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value


def test_retry_not_ready(client, storage_path):
    """Test retrying on NotReadyError."""
    count = Counter()

    @retry(max_time=1, max_tries=2, raise_on_giveup=False)
    def test_func(count):
        count.increment()
        raise NotReadyError("Not ready")

    test_func(count)

    assert count.value > 0


def test_retry_timeout_error(client, storage_path):
    """Test retrying on TimeoutError."""
    count = Counter()

    @retry(max_time=1, max_tries=20, raise_on_giveup=False)
    def test_func(count):
        count.increment()
        raise TimeoutError("Timeout")

    test_func(count)

    # Should give up immediately
    assert count.value == 1


def test_retry_hpserror_giveup(client, storage_path):
    """Test retrying on HPSError with give_up=True."""
    count = Counter()

    @retry(max_time=1, max_tries=20, raise_on_giveup=False)
    def test_func(count):
        count.increment()
        raise HPSError("HPSError", give_up=True)

    test_func(count)

    # Should give up immediately
    assert count.value == 1


def test_give_up_status(client, storage_path):
    """Test give_up_on status codes."""
    count = Counter()

    @retry(max_time=1, max_tries=20, raise_on_giveup=False)
    def test_func(count, code):
        resp = httpx.Response(status_code=code, request=httpx.Request("GET", "http://localhost"))
        raise_for_status(resp)
        count.increment()

    give_up_on = [401, 403]
    codes = give_up_on + [200, 202]
    for code in codes:
        test_func(count, code)

    # Should give up immediately
    assert count.value == len(give_up_on)
