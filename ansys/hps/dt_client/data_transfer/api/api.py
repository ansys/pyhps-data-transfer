import logging
import mimetypes
import os
import tempfile
import time
from typing import List

log = logging.getLogger(__name__)

import humanfriendly as hf

from ..client import Client
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
from ..models.ops import OperationState
from ..models.permissions import RoleAssignment, RoleQuery
from ..utils.jitter import get_expo_backoff
from .retry import retry


class DataTransferApi:
    def __init__(self, client: Client):
        self.dump_mode = "json"
        self.client = client

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    @retry()
    def status(self, wait=False):
        url = "/"
        while True:
            resp = self.client.session.get(url)
            json = resp.json()
            s = Status(**json)
            if wait and not s.ready:
                log.info("Waiting for the client to be ready...")
                time.sleep(1)
                continue
            return s

    def download_file(self, remote: str, path: str, dest: str = None):
        url = f"/data/{remote}/{path}"
        if not dest:
            dest = os.path.join(tempfile.gettempdir(), os.path.basename(path))
        with self.client.session.stream("GET", url) as resp:
            with open(dest, "wb") as file:
                for chunk in resp.iter_bytes():
                    file.write(chunk)
        return dest

    def upload_file(self, remote: str, path: str, src: str):
        url = f"/data/{remote}/{path}"
        filename = os.path.basename(src)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        resp = self.client.session.post(url, files={"file": (filename, open(src, "rb"), mime_type)})
        json = resp.json()
        return OpIdResponse(**json)

    @retry()
    def operations(self, ids: List[str]):
        url = "/operations"
        resp = self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

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
        log.warning("op id : %s", r.id)
        return r

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

    def wait_for(self, operation_ids: List[str], timeout: float | None = None, interval: float = 1.0):
        start = time.time()
        attempt = 0
        while True:
            attempt += 1
            ops = self.operations(operation_ids)
            if all(op.state in [OperationState.Succeeded, OperationState.Failed] for op in ops):
                break

            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for operations to complete")

            # TODO: Adjust based on transfer speed and file size
            duration = get_expo_backoff(interval, attempts=attempt, cap=10)
            log.debug(f"Waiting for {hf.format_timespan(duration)} ...")
            time.sleep(duration)
        return ops
