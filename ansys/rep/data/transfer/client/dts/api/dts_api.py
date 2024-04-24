import openapi_client
from openapi_client.models.rest_path_operations import RestPathOperations
from openapi_client.models.rest_src_dst import RestSrcDst
from openapi_client.models.rest_src_dst_operations import RestSrcDstOperations
from openapi_client.models.rest_storage_path import RestStoragePath
from pydantic import StrictStr, conlist

from ansys.rep.data.transfer.client.client import Client


class DtsApi:
    def __init__(self, client: Client):
        self.client = client

    # Status endpoints
    def status(self):
        return openapi_client.StatusApi(self.client).root_get()

    async def async_status(self):
        return openapi_client.StatusApi(self.client).root_get(async_req=True)

    # Operation endpoints
    def download_file(self, remote: StrictStr, path: StrictStr):
        return openapi_client.DataTransferApi(self.client).data_remote_path_get(remote, path)

    async def async_download_file(self, remote: StrictStr, path: StrictStr):
        return openapi_client.DataTransferApi(self.client).data_remote_path_get(remote, path, async_req=True)

    def upload_file(self, remote: StrictStr, path: StrictStr, file_path: StrictStr):
        return openapi_client.DataTransferApi(self.client).data_remote_path_post(remote, path, file_path)

    async def async_upload_file(self, remote: StrictStr, path: StrictStr, file_path: StrictStr):
        return openapi_client.DataTransferApi(self.client).data_remote_path_post(
            remote, path, file_path, async_req=True
        )

    # Storage endpoints
    def operations(self, ids: conlist(StrictStr)):
        return openapi_client.OperationsApi(self.client).operations_get(ids)

    async def async_operations(self, ids: conlist(StrictStr)):
        return openapi_client.OperationsApi(self.client).operations_get(ids, async_req=True)

    def storages(self):
        return openapi_client.StorageApi(self.client).storage_get()

    async def async_storages(self):
        return openapi_client.StorageApi(self.client).storage_get(async_req=True)

    def copy(self, operations: conlist(RestSrcDst)):
        return openapi_client.StorageApi(self.client).storagecopy_post(RestSrcDstOperations(operations=operations))

    async def async_copy(self, operations: conlist(RestSrcDst)):
        return openapi_client.StorageApi(self.client).storagecopy_post(
            RestSrcDstOperations(operations=operations), async_req=True
        )

    def exists(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storageexists_post(RestPathOperations(operations=operations))

    async def async_exists(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storageexists_post(
            RestPathOperations(operations=operations), async_req=True
        )

    def list(self, operations: conlist(RestSrcDst)):
        return openapi_client.StorageApi(self.client).storagelist_post(RestPathOperations(operations=operations))

    async def async_list(self, operations: conlist(RestSrcDst)):
        return openapi_client.StorageApi(self.client).storagelist_post(
            RestPathOperations(operations=operations), async_req=True
        )

    def mkdir(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storagemkdir_post(RestPathOperations(operations=operations))

    async def async_mkdir(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storagemkdir_post(
            RestPathOperations(operations=operations), async_req=True
        )

    def move(self, operations: conlist(RestSrcDst)):
        return openapi_client.StorageApi(self.client).storagemove_post(RestSrcDstOperations(operations=operations))

    async def async_move(self, operations: conlist(RestSrcDst)):
        return openapi_client.StorageApi(self.client).storagemove_post(
            RestSrcDstOperations(operations=operations), async_req=True
        )

    def remove(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storageremove_post(RestPathOperations(operations=operations))

    async def async_remove(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storageremove_post(
            RestPathOperations(operations=operations), async_req=True
        )

    def rmdir(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storagermdir_post(RestPathOperations(operations=operations))

    async def async_rmdir(self, operations: conlist(RestStoragePath)):
        return openapi_client.StorageApi(self.client).storage_get(
            RestPathOperations(operations=operations), async_req=True
        )
