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

"""Provides functionality for monitoring of operations."""

import logging
import time

from dateutil import parser
import humanfriendly as hf
import datetime

from ..models.ops import Operation, OperationState

log = logging.getLogger(__name__)


class DefaultOperationHandler:
    """Allows additional handling of the operations."""

    final = [OperationState.Succeeded, OperationState.Failed]

    def __init__(self):
        """Initializes the OperationHandler class object."""
        self.start = time.time()
        self.report_threshold = 10.0  # seconds

    def __call__(self, ops: list[Operation]):
        """Handle operations after they are fetched."""
        self._log_ops(ops)

    def _log_ops(self, ops: list[Operation]) -> str:
        so_far = time.time() - self.start
        num_running = 0
        for op in ops:
            for ch in op.children_detail or []:
                if ch.state not in self.final:
                    num_running += 1
                self._log_op(logging.DEBUG, ch)

            if op.state not in self.final:
                num_running += 1
            self._log_op(logging.INFO, op)

        if num_running > 0 and so_far > self.report_threshold:
            log.info(f"Waiting for {num_running} operations to complete. {hf.format_timespan(so_far)} so far ...")

    def _log_op(self, lvl: int, op: Operation):
        """Format the operation description."""
        op_type = "operation" if len(op.children) == 0 else "operation group"

        msg = f"{op_type.capitalize()} '{op.description}'({op.id})"

        op_done = op.state in self.final
        try:
            start = parser.parse(op.started_at)
            if op_done:
                end = parser.parse(op.ended_at)
            else:
                end = datetime.datetime.now(start.tzinfo)
            duration = (end - start).seconds
            durationStr = hf.format_timespan(end - start)
        except Exception as ex:
            log.debug(f"Failed to parse operation duration: {ex}")
            duration = 0
            durationStr = "unknown"

        state = op.state.value
        if op_done:
            msg += f" has {state} after {durationStr}"
            if op.info is not None:
                info = ", ".join([f"{k}={v}" for k, v in op.info.items()])
                msg += ", " + info
        else:
            msg += f" is {state}, {durationStr} so far, progress {op.progress:.2f}%"

        if op_done or duration > self.report_threshold:
            log.log(lvl, msg)


class AsyncOperationHandler(DefaultOperationHandler):
    """Asynchronous operation handler for operations."""

    def __init__(self):
        """Initializes the AsyncOperationHandler class object."""
        super().__init__()

    async def __call__(self, ops: list[Operation]):
        """Handle operations after they are fetched."""
        self._log_ops(ops)
