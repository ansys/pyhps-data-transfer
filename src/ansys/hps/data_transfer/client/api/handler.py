# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
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

import humanize as hz

from ..models import Operation, OperationState

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
        self.min_progress_interval = 15.0  # seconds
        self.last_progress = {}
        self.completed_ids = []

    def __call__(self, ops: list[Operation]):
        """Handle operations after they are fetched."""
        self._log_ops(ops)

    def _log_ops(self, ops: list[Operation]) -> str:
        # so_far = time.time() - self.start
        num_running = 0
        for op in ops:
            if op.children_detail is not None and self.Meta.expand_group:
                for ch in op.children_detail or []:
                    # For ops with lots of children, avoid logging completed children on every loop iteration
                    # If there are 29 small files and 1 large file in the group, we dont want to log 29 files
                    # are done 1000 times while the large file copies.
                    if ch.id not in self.completed_ids:
                        self._log_op(logging.DEBUG, ch)
                    if ch.state not in self.final:
                        num_running += 1
                    elif ch.id not in self.completed_ids:
                        self.completed_ids.append(ch.id)

            if op.state not in self.final:
                num_running += 1
            self._log_op(logging.INFO, op)

    def _log_op(self, lvl: int, op: Operation):
        """Format the operation description."""
        op_type = "operation" if op.children is None or len(op.children) == 0 else "operation group"
        op_done = op.state in self.final

        msg = f"Data transfer {op_type} '{op.description}'({op.id}) {'finished. ' if op_done else 'is in progress. '}"

        try:
            start = op.started_at
            if op_done:
                end = op.ended_at
            else:
                end = datetime.datetime.now(start.tzinfo)
            duration = (end - start).seconds
            duration_str = hz.precisedelta(end - start)
        except Exception as ex:
            log.debug(f"Failed to parse operation duration: {ex}")
            duration = 0
            duration_str = "unknown"

        # Initialize last progress time if not set, set it back in time
        # so it logs right away (report threshold) the first time.
        if self.last_progress.get(op.id, None) is None:
            self.last_progress[op.id] = time.time() - self.min_progress_interval

        state = op.state.value
        if op_done:
            msg += f"{state.title()} after {duration_str}"
            msg += self._info_str(op)
            # if op.messages:
            # msg += f', messages="{"; ".join(op.messages)}"'
            log.log(lvl, msg)
        elif duration > self.report_threshold and time.time() - self.last_progress[op.id] > self.min_progress_interval:
            self.last_progress[op.id] = time.time()
            msg += f"{state.title()} for {duration_str}"
            if op.progress and op.progress > 0.0:
                msg += f", progress {op.progress * 100.0:.1f}%"
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
