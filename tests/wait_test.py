# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

"""This module contains tests for verifying the performance, reliability, and correctness
of transferring large files using the Data Transfer API and Async Data Transfer API
from the Ansys HPS Data Transfer Client.
"""

import logging
import threading
import time

import psutil

from ansys.hps.data_transfer.client import DataTransferApi
from ansys.hps.data_transfer.client.models import OperationState

from .large_file_test import sync_copy

log = logging.getLogger(__name__)


def delayed_kill(delay: int, pid: int):
    time.sleep(delay)
    log.info(f"Killing process with pid {pid} ...")
    psutil.Process(pid).kill()


def test_wait_for_with_restart(storage_path, client):
    start_pid = client.pid
    kill = threading.Thread(
        target=delayed_kill,
        args=(
            2,
            start_pid,
        ),
    )

    api = DataTransferApi(client)
    op, manager = sync_copy(storage_path, api)
    assert op.id is not None

    kill.start()

    op = api.wait_for(op.id)
    assert op[0].state == OperationState.Succeeded, op[0].messages

    resp = api.status()
    assert resp.build_info is not None

    # Verify that the client process has been restarted
    assert client.pid != start_pid

    manager.delete_file()
