# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#

import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ansys.hps.data_transfer.client.api.api import DataTransferApi
from ansys.hps.data_transfer.client.binary import Binary, BinaryConfig
from ansys.hps.data_transfer.client.client import ClientBase
from ansys.hps.data_transfer.client.exceptions import TimeoutError
from ansys.hps.data_transfer.client.models import OperationState


class _DummyThread:
    def __init__(self, alive=True):
        self._alive = alive
        self.join = MagicMock()

    def is_alive(self):
        return self._alive


def test_binary_monitor_handles_stuck_log_thread_and_stdout_close_error():
    config = BinaryConfig(path="/tmp/worker", monitor_interval=0.01, max_restarts=5)
    binary = Binary(config=config)
    binary._stop = threading.Event()
    binary._prepared = threading.Event()

    stdout = MagicMock()
    stdout.close.side_effect = RuntimeError("close failure")
    process = MagicMock()
    process.poll.return_value = 9
    process.stdout = stdout
    binary._process = process

    binary._log_thread = _DummyThread(alive=True)
    binary.config._on_process_died = lambda _code: binary._stop.set()

    with (
        patch("ansys.hps.data_transfer.client.binary.time.sleep", return_value=None),
        patch("ansys.hps.data_transfer.client.binary.log") as log_mock,
    ):
        binary._monitor()

    stdout.close.assert_called_once()
    binary._log_thread = None
    assert any(
        call.args and "Log thread did not stop in time" in call.args[0] for call in log_mock.warning.call_args_list
    )


def test_binary_stop_suppresses_worker_stopped_log_when_stopping():
    binary = Binary(config=BinaryConfig(path="/tmp/worker"))
    binary._process = MagicMock()
    binary._process.poll.return_value = 0
    binary._stop = threading.Event()
    binary._stop.set()
    binary._prepared = threading.Event()

    with patch("ansys.hps.data_transfer.client.binary.log") as log_mock:
        binary.stop(wait=0.01)

    assert not any(call.args and call.args[0] == "Worker stopped." for call in log_mock.debug.call_args_list)


def test_binary_log_output_suppresses_eof_log_during_stop():
    binary = Binary(config=BinaryConfig(path="/tmp/worker"))
    binary._stop = threading.Event()
    binary._prepared = threading.Event()

    stdout = MagicMock()

    def _readline():
        binary._stop.set()
        return b""

    stdout.readline.side_effect = _readline
    binary._process = MagicMock(stdout=stdout)

    with patch("ansys.hps.data_transfer.client.binary.log") as log_mock:
        binary._log_output()

    assert not any(
        call.args and "Log thread stdout ended normally" in call.args[0] for call in log_mock.debug.call_args_list
    )


def test_on_port_changed_closes_async_session_without_running_loop():
    client = ClientBase()
    session = MagicMock()
    session.close = None
    session.aclose = MagicMock(return_value=object())
    client._session = session

    with (
        patch(
            "ansys.hps.data_transfer.client.client.asyncio.get_running_loop",
            side_effect=RuntimeError,
        ),
        patch("ansys.hps.data_transfer.client.client.asyncio.run") as run_mock,
    ):
        client._on_port_changed(12345)

    run_mock.assert_called_once()
    assert client._session is None


def test_on_port_changed_logs_warning_when_close_fails():
    client = ClientBase()
    session = MagicMock()
    session.close.side_effect = RuntimeError("boom")
    client._session = session

    with patch("ansys.hps.data_transfer.client.client.log") as log_mock:
        client._on_port_changed(12345)

    assert any(
        call.args and "Failed to close session on port change" in call.args[0]
        for call in log_mock.warning.call_args_list
    )
    assert client._session is None


def test_response_hook_returns_early_when_monitor_stopping():
    client = ClientBase()
    client._monitor_stop = threading.Event()
    client._monitor_stop.set()
    client.refresh_token_callback = MagicMock(return_value="new-token")

    response = MagicMock()
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}

    client._auto_refresh_token(response)

    client.refresh_token_callback.assert_not_called()


@pytest.mark.asyncio
async def test_async_response_hook_returns_early_when_monitor_stopping():
    client = ClientBase()
    client._monitor_stop = threading.Event()
    client._monitor_stop.set()
    client.refresh_token_callback = AsyncMock(return_value="new-token")

    response = MagicMock()
    response.status_code = 401
    response.request = MagicMock()
    response.request.headers = {}

    await client._async_auto_refresh_token(response)

    client.refresh_token_callback.assert_not_called()


def test_wait_for_raises_on_prolonged_status_unavailability_with_timeout():
    api = DataTransferApi(client=MagicMock())
    running = [SimpleNamespace(state=OperationState.Running)]
    api._operations = MagicMock(side_effect=[running, Exception("status down")])

    time_values = [0.0, 1.0, 32.0]

    def _time():
        return time_values.pop(0) if time_values else 32.0

    with (
        patch("ansys.hps.data_transfer.client.api.api.time.time", side_effect=_time),
        patch("ansys.hps.data_transfer.client.api.api.time.sleep", return_value=None),
    ):
        with pytest.raises(TimeoutError, match="Operation status unavailable"):
            api.wait_for(["op-1"], timeout=60.0, interval=0.0, cap=0.0, handler=lambda _ops: None)


def test_wait_for_returns_last_known_ops_on_prolonged_unavailability_without_timeout():
    api = DataTransferApi(client=MagicMock())
    running = [SimpleNamespace(state=OperationState.Running)]
    api._operations = MagicMock(side_effect=[running, Exception("status down")])

    time_values = iter([0.0, 1.0, 32.0])
    with (
        patch(
            "ansys.hps.data_transfer.client.api.api.time.time",
            side_effect=lambda: next(time_values),
        ),
        patch("ansys.hps.data_transfer.client.api.api.time.sleep", return_value=None),
        patch("ansys.hps.data_transfer.client.api.api.log") as log_mock,
    ):
        ops = api.wait_for(["op-1"], timeout=None, interval=0.0, cap=0.0, handler=lambda _ops: None)

    assert ops == running
    assert any(
        call.args and "Returning last known operation status" in call.args[0]
        for call in log_mock.warning.call_args_list
    )
