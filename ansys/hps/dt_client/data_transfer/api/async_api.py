import mimetypes
import os
import tempfile
from typing import List

from ..client import AsyncClient
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
from ..models.permissions import RoleAssignment, RoleQuery


class AsyncDataTransferApi:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def status(self):
        url = "/"
        resp = await self.client.session.get(url)
        json = resp.json()
        return Status(**json)

    async def download_file(self, remote: str, path: str, dest: str = None):
        url = f"/data/{remote}/{path}"
        if not dest:
            dest = os.path.join(tempfile.gettempdir(), os.path.basename(path))
        async with self.client.session.stream("GET", url) as resp:
            with open(dest, "wb") as file:
                async for chunk in resp.aiter_bytes():
                    file.write(chunk)
        return dest

    async def upload_file(self, remote: str, path: str, file_path: str):
        url = f"/data/{remote}/{path}"
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        resp = await self.client.session.post(url, files={"file": (filename, open(file_path, "rb"), mime_type)})
        json = resp.json()
        return OpIdResponse(**json)

    async def operations(self, ids: List[str]):
        url = "/operations"
        resp = await self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    async def storages(self):
        url = "/storage"
        resp = await self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    async def copy(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("copy", operations)

    async def exists(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("exists", operations)

    async def list(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("list", operations)

    async def mkdir(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("mkdir", operations)

    async def move(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("move", operations)

    async def remove(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("remove", operations)

    async def rmdir(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("rmdir", operations)

    async def _exec_async_operation_req(self, storage_operation: str, operations: List[StoragePath] | List[SrcDst]):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump() for operation in operations]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    async def check_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump() for permission in permissions]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    async def get_permissions(self, permissions: List[RoleQuery]):
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump() for permission in permissions]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    async def remove_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump() for permission in permissions]}
        await self.client.session.post(url, json=payload)
        return None

    async def set_permissions(self, permissions: List[RoleAssignment]):
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump() for permission in permissions]}
        await self.client.session.post(url, json=payload)
        return None
