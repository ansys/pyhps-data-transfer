import mimetypes
import os
import tempfile
from typing import List

from ansys.rep.data.transfer.client.client import Client
from ansys.rep.data.transfer.client.dtsc.models.rest import (
    OpIdResponse,
    OpsResponse,
    SrcDst,
    Status,
    StorageConfigResponse,
    StoragePath,
)


class DtscApi:
    def __init__(self, client: Client):
        self.client = client

    def status(self):
        url = "/"
        resp = self.client.session.get(url)
        json = resp.json()
        return Status(**json)

    async def async_status(self):
        url = "/"
        resp = await self.client.session.get(url)
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

    async def async_download_file(self, remote: str, path: str, dest: str = None):
        url = f"/data/{remote}/{path}"
        if not dest:
            dest = os.path.join(tempfile.gettempdir(), os.path.basename(path))
        async with self.client.session.stream("GET", url) as resp:
            with open(dest, "wb") as file:
                async for chunk in resp.aiter_bytes():
                    file.write(chunk)
        return dest

    def upload_file(self, remote: str, path: str, file_path: str):
        url = f"/data/{remote}/{path}"
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        resp = self.client.session.post(url, files={"file": (filename, open(file_path, "rb"), mime_type)})
        json = resp.json()
        return OpIdResponse(**json)

    async def async_upload_file(self, remote: str, path: str, file_path: str):
        url = f"/data/{remote}/{path}"
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        resp = await self.client.session.post(url, files={"file": (filename, open(file_path, "rb"), mime_type)})
        json = resp.json()
        return OpIdResponse(**json)

    def operations(self, ids: List[str]):
        url = "/operations"
        resp = self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    async def async_operations(self, ids: List[str]):
        url = "/operations"
        resp = await self.client.session.get(url, params={"ids": ids})
        json = resp.json()
        return OpsResponse(**json).operations

    def storages(self):
        url = "/storage"
        resp = self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    async def async_storages(self):
        url = "/storage"
        resp = await self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    def copy(self, operations: List[SrcDst]):
        return self._exec_operation_req("copy", operations)

    async def async_copy(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("copy", operations)

    def exists(self, operations: List[StoragePath]):
        return self._exec_operation_req("exists", operations)

    async def async_exists(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("exists", operations)

    def list(self, operations: List[SrcDst]):
        return self._exec_operation_req("list", operations)

    async def async_list(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("list", operations)

    def mkdir(self, operations: List[StoragePath]):
        return self._exec_operation_req("mkdir", operations)

    async def async_mkdir(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("mkdir", operations)

    def move(self, operations: List[SrcDst]):
        return self._exec_operation_req("move", operations)

    async def async_move(self, operations: List[SrcDst]):
        return await self._exec_async_operation_req("move", operations)

    def remove(self, operations: List[StoragePath]):
        return self._exec_operation_req("remove", operations)

    async def async_remove(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("remove", operations)

    def rmdir(self, operations: List[StoragePath]):
        return self._exec_operation_req("rmdir", operations)

    async def async_rmdir(self, operations: List[StoragePath]):
        return await self._exec_async_operation_req("rmdir", operations)

    def _exec_operation_req(self, storage_operation: str, operations: List[StoragePath] | List[SrcDst]):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump() for operation in operations]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    async def _exec_async_operation_req(self, storage_operation: str, operations: List[StoragePath] | List[SrcDst]):
        url = f"/storage:{storage_operation}"
        payload = {"operations": [operation.model_dump() for operation in operations]}
        resp = await self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)
