import logging
import mimetypes
import os
import tempfile
import time
import traceback
from typing import List

import backoff

log = logging.getLogger(__name__)

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


def _on_backoff(details, exc_info=False):
    try:
        msg = "Backing off {wait:0.1f} seconds after {tries} tries: {exception}".format(**details)
        log.info(msg)
        if exc_info:
            try:
                ex_str = "\n".join(traceback.format_exception(details["exception"]))
                log.debug(f"Backoff caused by:\n{ex_str}")
            except:
                pass
    except Exception as ex:
        log.warning(f"Failed to log in backoff handler: {ex}")


class DataTransferApi:
    def __init__(self, client: Client):
        self.dump_mode = "json"
        self.client = client

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=30,
        max_time=60,
        jitter=backoff.full_jitter,
        raise_on_giveup=True,
        on_backoff=_on_backoff,
        logger=None,
    )
    def status(self, wait=False, timeout=None):
        url = "/"
        while True:
            resp = self.client.session.get(url)
            json = resp.json()
            s = Status(**json)
            if wait and not s.ready:
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

    def _exec_operation_req(self, storage_operation: str, operations: List[StoragePath] | List[SrcDst]):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump(mode=self.dump_mode) for operation in operations]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        r = OpIdResponse(**json)
        log.warning("op id : %s", r.id)
        return r

    def check_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    def get_permissions(self, permissions: List[RoleQuery]):
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    def remove_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)
        return None

    def set_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)
        return None

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=30,
        max_time=60,
        jitter=backoff.full_jitter,
        raise_on_giveup=True,
        on_backoff=_on_backoff,
        logger=None,
    )
    def wait_for(self, operation_ids: List[str], timeout: float | None = None, interval: float = 1.0):
        start = time.time()
        while True:
            ops = self.operations(operation_ids)
            if all(op.state in [OperationState.Succeeded, OperationState.Failed] for op in ops):
                break

            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for operations to complete")
            time.sleep(interval)
        return ops
