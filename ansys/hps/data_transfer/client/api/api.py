import logging
import textwrap
import time
from typing import Dict, List

import backoff

log = logging.getLogger(__name__)

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


class DataTransferApi:
    def __init__(self, client: Client):
        self.dump_mode = "json"
        self.client = client

    @retry()
    def status(self, wait=False, sleep=5, jitter=True, timeout: float | None = 20.0):
        def _sleep():
            log.info(f"Waiting for the worker to be ready on port {self.client.binary_config.port} ...")
            s = backoff.full_jitter(sleep) if jitter else sleep
            time.sleep(s)

        url = "/"
        start = time.time()
        while True:
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for worker to be ready")

            resp = self.client.session.get(url)
            json = resp.json()
            s = Status(**json)
            if wait and not s.ready:
                _sleep()
                continue
            return s

    @retry()
    def operations(self, ids: List[str]):
        return self._operations(ids)

    def storages(self):
        url = "/storage"
        resp = self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    def copy(self, operations: List[SrcDst]):
        return self._exec_operation_req("copy", operations)

    def exists(self, operations: List[StoragePath]):
        return self._exec_operation_req("exists", operations)

    def list(self, operations: List[StoragePath]):
        return self._exec_operation_req("list", operations)

    def mkdir(self, operations: List[StoragePath]):
        return self._exec_operation_req("mkdir", operations)

    def move(self, operations: List[SrcDst]):
        return self._exec_operation_req("move", operations)

    def remove(self, operations: List[StoragePath]):
        return self._exec_operation_req("remove", operations)

    def rmdir(self, operations: List[StoragePath]):
        return self._exec_operation_req("rmdir", operations)

    @retry()
    def _exec_operation_req(self, storage_operation: str, operations: List[StoragePath] | List[SrcDst]):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump(mode=self.dump_mode) for operation in operations]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        r = OpIdResponse(**json)
        return r

    def _operations(self, ids: List[str]):
        url = "/operations"
        resp = self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    @retry()
    def check_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    @retry()
    def get_permissions(self, permissions: List[RoleQuery]):
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    @retry()
    def remove_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)
        return None

    @retry()
    def set_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)
        return None

    @retry()
    def get_metadata(self, paths: List[str | StoragePath]):
        url = "/metadata:get"
        paths = [p if isinstance(p, str) else p.path for p in paths]
        payload = {"paths": paths}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    @retry()
    def set_metadata(self, asgs: Dict[str | StoragePath, DataAssignment]):
        url = "/metadata:set"
        d = {k if isinstance(k, str) else k.path: v for k, v in asgs.items()}
        req = SetMetadataRequest(metadata=d)
        resp = self.client.session.post(url, json=req.model_dump(mode=self.dump_mode))
        json = resp.json()
        return OpIdResponse(**json)

    def wait_for(
        self,
        operation_ids: List[str | Operation | OpIdResponse],
        timeout: float | None = None,
        interval: float = 0.1,
        cap: float = 2.0,
    ):
        if not isinstance(operation_ids, list):
            operation_ids = [operation_ids]
        operation_ids = [op.id if isinstance(op, (Operation, OpIdResponse)) else op for op in operation_ids]
        start = time.time()
        attempt = 0
        op_str = textwrap.wrap(", ".join(operation_ids), width=60, placeholder="...")
        # log.debug(f"Waiting for operations to complete: {op_str}")
        while True:
            attempt += 1
            try:
                ops = self._operations(operation_ids)
                if self.client.binary_config.debug:
                    so_far = hf.format_timespan(time.time() - start)
                    log.debug(f"Waiting for {len(operation_ids)} operations to complete, {so_far} so far")
                    for op in ops:
                        fields = [
                            f"id={op.id}",
                            f"state={op.state}",
                            f"start={op.started_at}",
                            f"succeeded_on={op.succeeded_on}",
                        ]
                        log.debug(f"- Operation '{op.description}' {' '.join(fields)}")
                if all(op.state in [OperationState.Succeeded, OperationState.Failed] for op in ops):
                    break
            except Exception as e:
                log.debug(f"Error getting operations: {e}")

            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for operations to complete")

            # TODO: Adjust based on transfer speed and file size
            duration = get_expo_backoff(interval, attempts=attempt, cap=cap, jitter=True)
            log.debug(f"Waiting for {hf.format_timespan(duration)} before retrying ...")
            time.sleep(duration)

        duration = hf.format_timespan(time.time() - start)
        log.debug(f"Operations completed after {duration}: {op_str}")
        return ops
