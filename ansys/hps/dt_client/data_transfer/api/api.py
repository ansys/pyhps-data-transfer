import mimetypes
import os
import tempfile
from typing import List

from ..client import Client
from ..models.permissions import RoleAssignment, RoleQuery
from ..models.rest import (
    CheckPermissionsResponse,
    GetPermissionsResponse,
    OpIdResponse,
    OpsResponse,
    RemovePermissionsRequest,
    SrcDst,
    Status,
    StorageConfigResponse,
    StoragePath,
)


class DataTransferApi:
    def __init__(self, client: Client):
        self.client = client

    def status(self):
        url = "/"
        resp = self.client.session.get(url)
        json = resp.json()
        return Status(**json)

    def download_file(self, remote: str, path: str, dest: str = None):
        url = f"/data/{remote}/{path}"
        if not dest:
            dest = os.path.join(tempfile.gettempdir(), os.path.basename(path))
        with self.client.session.stream("GET", url) as resp:
            with open(dest, "wb") as file:
                for chunk in resp.iter_bytes():
                    file.write(chunk)
        return dest

    def upload_file(self, remote: str, path: str, file_path: str):
        url = f"/data/{remote}/{path}"
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        resp = self.client.session.post(url, files={"file": (filename, open(file_path, "rb"), mime_type)})
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

    def list(self, operations: List[SrcDst]):
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
        payload = {"operations": [operation.model_dump() for operation in operations]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    def check_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:check"
        payload = {"permissions": permissions}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    def get_permissions(self, permissions: List[RoleQuery]):
        url = "/permissions:get"
        payload = {"permissions": permissions}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    def remove_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:remove"
        payload = {"permissions": permissions}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return RemovePermissionsRequest(**json)

    def set_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:set"
        payload = {"permissions": permissions}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)
