import builtins
from collections.abc import Callable
import logging
import textwrap
import traceback
import time

import backoff
import humanfriendly as hf

from ..client import Client
from ..exceptions import TimeoutError
from ..models.metadata import DataAssignment
from ..models.msg import (
    CheckPermissionsResponse,
    GetPermissionsResponse,
    OpIdResponse,
    OpsResponse,
    SetMetadataRequest,
    SrcDst,
    Status,
    StorageConfigResponse,
    StoragePath,
)
from ..models.ops import Operation, OperationState
from ..models.permissions import RoleAssignment, RoleQuery
from ..utils.jitter import get_expo_backoff
from .retry import retry
from dateutil import parser

log = logging.getLogger(__name__)


class DefaultOperationHandler:
    """Allows additional handling of the operations."""

    class Meta:
        """Meta class for DefaultOperationHandler."""
        expand_groups = True

    def __init__(self):
        """Initializes the OperationHandler class object."""
        self.start = time.time()
        self.report_threshold = 10.0  # seconds

    def __call__(self, ops: list[Operation]):
        """Handle operations after they are fetched."""
        self._log_ops(ops)

    def _log_ops(self, ops: list[Operation]) -> str:
        so_far = time.time() - self.start
        done_ops = [op.state for op in ops if op.state in [OperationState.Succeeded, OperationState.Failed]]
        for op in ops:
            if op.state in [OperationState.Succeeded, OperationState.Failed]:
                log.info(self._format_op(op))
            elif so_far > self.report_threshold:
                self._format_op(op, progress=True)

        num_running = len(ops) - len(done_ops)
        # num_completed = len(done_ops)
        if num_running > 0 and so_far > self.report_threshold:
            log.info(f"Waiting for {num_running} operations to complete. {hf.format_timespan(so_far)} so far ...")
        # elif num_completed == len(ops):
        #     duration = hf.format_timespan(time.time() - self.start)
        #     log.debug(f"Completed {num_completed} operations after {duration}")

    def _format_op(self, op: Operation) -> str:
        """Format the operation description."""
        op_type = "operation" if len(op.children) == 0 else "operation group"
        
        msg = f"{op_type.capitalize()} '{op.description}'({op.id})"

        try:
            start = parser.parse(op.started_at)
            end = parser.parse(op.ended_at)
            duration = hf.format_timespan(end - start)
        except Exception:
            duration = "unknown"

        state = op.state.value
        if op.state in [OperationState.Succeeded, OperationState.Failed]:
            msg += f" has {state} after {duration}"
        else:
            msg += f" is {state}, {duration} so far, progress {op.progress:.2f}%"

        if op.info is not None:
            info = ", ".join([f"{k}={v}" for k, v in op.info.items()])
            msg += ", " + info
        return msg

class AsyncOperationHandler(DefaultOperationHandler):
    """Asynchronous operation handler for operations."""

    def __init__(self): 
        """Initializes the AsyncOperationHandler class object."""
        super().__init__()
   
    async def __call__(self, ops: list[Operation]):
        self._log_ops(ops)