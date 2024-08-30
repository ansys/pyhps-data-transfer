# generated by datamodel-codegen

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from . import ops
from . import permissions as perms  # noqa: F401


class BinaryInfo(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    type: Optional[str] = None


class BuildInfo(BaseModel):
    branch: Optional[str] = None
    mode: Optional[str] = None
    revision: Optional[str] = None
    short_revision: Optional[str] = None
    version: Optional[str] = None
    version_hash: Optional[str] = None


class CheckPermissionsResponse(BaseModel):
    allowed: Optional[bool] = None


class OpIdResponse(BaseModel):
    id: Optional[str] = "2diK2kCkpgeHAQSNthIZ1JYyPte"
    location: Optional[str] = "/api/v1/operations/2diK2kCkpgeHAQSNthIZ1JYyPte"


class OpsRequest(BaseModel):
    ids: List[str]


class PermissionsConfigResponse(BaseModel):
    config: Optional[Dict[str, Any]] = None


class Status(BaseModel):
    build_info: Optional[BuildInfo] = None
    ready: Optional[bool] = None
    time: Optional[str] = None


class StorageConfigResponse(BaseModel):
    storage: Optional[List[Dict[str, Any]]] = None


class StoragePath(BaseModel):
    path: str
    remote: Optional[str] = "any"


class Binaries(BaseModel):
    available: Optional[List[BinaryInfo]] = None


class PathOperations(BaseModel):
    operations: List[StoragePath]


class SrcDst(BaseModel):
    dst: StoragePath
    src: StoragePath


class SrcDstOperations(BaseModel):
    operations: List[SrcDst]


class OpsResponse(BaseModel):
    operations: Optional[List[ops.Operation]] = None


class CheckPermissionsRequest(BaseModel):
    permissions: Optional[List[perms.RoleAssignment]] = None


class GetPermissionsRequest(BaseModel):
    permissions: Optional[List[perms.RoleQuery]] = None


class GetPermissionsResponse(BaseModel):
    permissions: Optional[List[perms.RoleAssignment]] = None


class RemovePermissionsRequest(BaseModel):
    permissions: Optional[List[perms.RoleAssignment]] = None


class SetPermissionsRequest(BaseModel):
    permissions: Optional[List[perms.RoleAssignment]] = None
