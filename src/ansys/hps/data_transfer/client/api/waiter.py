# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons who the Software is
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

"""Server-Sent Events (SSE) waiter for real-time operation monitoring."""

from collections.abc import Awaitable, Callable
import json
import logging
import time
from uuid import uuid4

from ..models import Operation, OperationState

log = logging.getLogger(__name__)

SSE_EVENT_TYPES = ["operation:updated", "operation:completed"]
SILENCE_TIMEOUT = 30.0  # seconds before considering SSE stream dead


class SseWaiter:
    """Context manager that subscribes to SSE events for one or more operation subjects.

    Parameters
    ----------
    session : httpx.Client
        The HTTP session to use for the SSE connection.
    subjects : list[str] | str
        One or more subject IDs to filter events.
    handler : Callable[[list[Operation]], None] | None
        Optional callback invoked with each operation update.
    timeout : float
        Silence timeout in seconds. If no events received for this duration,
        the stream is considered dead. Default 30s.
    """

    def __init__(
        self,
        session,
        subjects: list[str] | str,
        handler: Callable[[list[Operation]], None] | None = None,
        timeout: float = SILENCE_TIMEOUT,
    ):
        """Initialize the SSE waiter with a session, subjects, and optional handler."""
        self.session = session
        self.subjects = [subjects] if isinstance(subjects, str) else subjects
        self.handler = handler
        self.timeout = timeout
        self._stream_ctx = None
        self._response = None
        self._terminal = False
        self._last_event_time = time.time()

    def __enter__(self):
        """Open the SSE stream connection."""
        params = {"event_types": SSE_EVENT_TYPES}
        if len(self.subjects) > 1:
            params["subject"] = self.subjects
        elif len(self.subjects) == 1:
            params["subject"] = self.subjects[0]

        self._stream_ctx = self.session.stream("GET", "/events", params=params, timeout=35.0)
        self._response = self._stream_ctx.__enter__()
        self._last_event_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the SSE stream connection."""
        if self._response:
            self._response.close()
            self._response = None
        if self._stream_ctx:
            self._stream_ctx.__exit__(exc_type, exc_val, exc_tb)
            self._stream_ctx = None
        return False

    def __iter__(self):
        """Return an iterator over parsed SSE operation updates."""
        return self._parse()

    def _parse(self):
        """Parse SSE events and yield Operation objects."""
        for line in self._response.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                self._last_event_time = time.time()
                try:
                    data = json.loads(line[6:])
                    op_data = data.get("data", {})
                    op = Operation(**op_data)
                    if self.handler:
                        try:
                            self.handler([op])
                        except Exception as e:
                            log.warning(f"SSE handler error: {e}")
                    yield op
                    if op.state in (OperationState.Succeeded, OperationState.Failed):
                        self._terminal = True
                        return
                except json.JSONDecodeError as e:
                    log.warning(f"Failed to parse SSE data: {e}")
                except Exception as e:
                    log.warning(f"Error processing SSE event: {e}")

    @property
    def is_terminal(self) -> bool:
        """Whether a terminal event (Succeeded/Failed) has been received."""
        return self._terminal

    @property
    def time_since_last_event(self) -> float:
        """Seconds since the last SSE event was received."""
        return time.time() - self._last_event_time


class AsyncSseWaiter:
    """Async version of SseWaiter for use with AsyncClient."""

    def __init__(
        self,
        session,
        subjects: list[str] | str,
        handler: Callable[[list[Operation]], Awaitable[None]] | None = None,
        timeout: float = SILENCE_TIMEOUT,
    ):
        """Initialize the async SSE waiter with a session, subjects, and optional handler."""
        self.session = session
        self.subjects = [subjects] if isinstance(subjects, str) else subjects
        self.handler = handler
        self.timeout = timeout
        self._stream_ctx = None
        self._response = None
        self._terminal = False
        self._last_event_time = time.time()

    async def __aenter__(self):
        """Open the SSE stream connection."""
        params = {"event_types": SSE_EVENT_TYPES}
        if len(self.subjects) > 1:
            params["subject"] = self.subjects
        elif len(self.subjects) == 1:
            params["subject"] = self.subjects[0]

        self._stream_ctx = await self.session.stream("GET", "/events", params=params, timeout=35.0)
        self._response = await self._stream_ctx.__aenter__()
        self._last_event_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the SSE stream connection."""
        if self._response:
            await self._response.aclose()
            self._response = None
        if self._stream_ctx:
            await self._stream_ctx.__aexit__(exc_type, exc_val, exc_tb)
            self._stream_ctx = None
        return False

    def __aiter__(self):
        """Return an async iterator over parsed SSE operation updates."""
        return self._parse()

    async def _parse(self):
        """Parse SSE events asynchronously and yield Operation objects."""
        async for line in self._response.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                self._last_event_time = time.time()
                try:
                    data = json.loads(line[6:])
                    op_data = data.get("data", {})
                    op = Operation(**op_data)
                    if self.handler:
                        try:
                            await self.handler([op])
                        except Exception as e:
                            log.warning(f"Async SSE handler error: {e}")
                    yield op
                    if op.state in (OperationState.Succeeded, OperationState.Failed):
                        self._terminal = True
                        return
                except json.JSONDecodeError as e:
                    log.warning(f"Failed to parse SSE data: {e}")
                except Exception as e:
                    log.warning(f"Error processing SSE event: {e}")

    @property
    def is_terminal(self) -> bool:
        """Whether a terminal event (Succeeded/Failed) has been received."""
        return self._terminal

    @property
    def time_since_last_event(self) -> float:
        """Seconds since the last SSE event was received."""
        return time.time() - self._last_event_time


def generate_subject() -> str:
    """Generate a unique subject ID for SSE subscription."""
    return uuid4().hex
