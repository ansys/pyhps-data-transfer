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

import datetime
import logging
import time

from dateutil import parser
import humanfriendly as hf

from ..models.ops import Operation, OperationState

log = logging.getLogger(__name__)


class WaitHandler:
    """Allows additional handling of operation status on wait."""

    class Meta:
        """Meta class for WaitHandler."""
        expand_group = True

    final = [OperationState.Succeeded, OperationState.Failed]

    def __init__(self):
        """Initializes the WaitHandler class object."""
        self.start = time.time()
        self.report_threshold = 2.0  # seconds
        self.min_progress_interval = 3.0  # seconds
        self.last_progress = self.start

    def __call__(self, ops: list[Operation]):
        """Handle operations after they are fetched."""
        self._log_ops(ops)

    def _log_ops(self, ops: list[Operation]) -> str:
        # so_far = time.time() - self.start
        num_running = 0
        for op in ops:
            for ch in op.children_detail or []:
                if ch.state not in self.final:
                    num_running += 1
                self._log_op(logging.DEBUG, ch)

            if op.state not in self.final:
                num_running += 1
            self._log_op(logging.INFO, op)

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
            duration_str = hf.format_timespan(end - start)
        except Exception as ex:
            log.debug(f"Failed to parse operation duration: {ex}")
            duration = 0
            duration_str = "unknown"

        state = op.state.value
        if op_done:
            msg += f" has {state} after {duration_str}"
            msg += self._info_str(op)
            # if op.messages:
            # msg += f', messages="{"; ".join(op.messages)}"'
            log.log(lvl, msg)
        elif duration > self.report_threshold and time.time() - self.last_progress > self.min_progress_interval:
            self.last_progress = time.time()
            msg += f" is {state}, {duration_str} so far"
            if op.progress_current > 0:
                msg += f", progress {op.progress*100.0:.1f}%"
            msg += self._info_str(op)
            log.log(lvl, msg)

    
    def _info_str(self, op: Operation) -> str:
        """Format the operation info."""
        if not op.info:
            return ""
        info = ", ".join([f"{k}={v}" for k, v in op.info.items()])
        return f", {info}"


class AsyncWaitHandler(WaitHandler):
    """Allows additional, asynchronous handling of operation status on wait."""

    def __init__(self):
        """Initializes the AsyncOperationHandler class object."""
        super().__init__()

    async def __call__(self, ops: list[Operation]):
        """Handle operations after they are fetched."""
        self._log_ops(ops)
