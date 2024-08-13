import asyncio
import logging
import textwrap
import time
from typing import List

import backoff
import humanfriendly as hf

from ..client import AsyncClient
from ..exceptions import TimeoutError
from ..models.msg import (
    CheckPermissionsResponse,
    GetPermissionsResponse,
    OpIdResponse,
    OpsResponse,
    SrcDst,
    Status,
    StorageConfigResponse,
    StoragePath,
)
from ..models.ops import Operation, OperationState
from ..models.permissions import RoleAssignment, RoleQuery
from ..utils.jitter import get_expo_backoff
from .retry import retry

log = logging.getLogger(__name__)


class AsyncDataTransferApi:
    def __init__(self, client: AsyncClient):
        self.dump_mode = "json"
        self.client = client

    @retry()
    async def status(self, wait=False, sleep=5, jitter=True, timeout: float | None = 60.0):
        async def _sleep():
            log.info("Waiting for the worker to be ready...")
            s = backoff.full_jitter(sleep) if jitter else sleep
            await asyncio.sleep(s)

        url = "/"
        start = time.time()
        while True:
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for client to be ready")

            try:
                resp = await self.client.session.get(url)
                json = resp.json()
                s = Status(**json)
                if wait and not s.ready:
                    await _sleep()
                    continue
                return s
            except Exception as e:
                log.debug(f"Error getting status: {e}")
                await _sleep()

    @retry()
    async def operations(self, ids: List[str]):
        return await self._operations(ids)

    async def storages(self):
        url = "/storage"
        resp = await self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    async def copy(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("copy", operations)

    async def exists(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("exists", operations)

    async def list(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("list", operations)

    async def mkdir(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("mkdir", operations)

    async def move(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("move", operations)

    async def remove(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("remove", operations)

    async def rmdir(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("rmdir", operations)

    @retry()
    async def _exec_async_operation_req(self, storage_operation: str, operations: List[StoragePath] | List[SrcDst]):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump(mode=self.dump_mode) for operation in operations]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    async def _operations(self, ids: List[str]):
        url = "/operations"
        resp = await self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    @retry()
    async def check_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    @retry()
    async def get_permissions(self, permissions: List[RoleQuery]):
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    @retry()
    async def remove_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        await self.client.session.post(url, json=payload)
        return None

    @retry()
    async def set_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        await self.client.session.post(url, json=payload)
        return None

    @retry()
    async def get_metadata(self, operations: List[StoragePath]):
        url = "/metadata:get"
        payload = {"operations": [operation.model_dump(mode=self.dump_mode) for operation in operations]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    async def wait_for(self, operation_ids: List[str | Operation], timeout: float | None = None, interval: float = 0.2):
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
                ops = await self._operations(operation_ids)
                if all(op.state in [OperationState.Succeeded, OperationState.Failed] for op in ops):
                    break
            except Exception as e:
                log.debug(f"Error getting operations: {e}")

            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for operations to complete")

            # TODO: Adjust based on transfer speed and file size
            duration = get_expo_backoff(interval, attempts=attempt, cap=interval * 2.0)
            if self.client.binary_config.debug:
                so_far = hf.format_timespan(time.time() - start)
                log.debug(f"Waiting for {len(operation_ids)} operations to complete, {so_far} so far")
                for op in ops:
                    log.debug(f"- Operation '{op.description}' id={op.id} state={op.state} start={op.started_at}")
            log.debug(f"Sleeping for {hf.format_timespan(duration)} ...")

            await asyncio.sleep(duration)

        duration = hf.format_timespan(time.time() - start)
        log.debug(f"Operations completed after {duration}: {op_str}")
        return ops
