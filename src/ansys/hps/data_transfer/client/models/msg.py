# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from . import metadata, ops


class BuildInfo(BaseModel):
    branch: Optional[str] = None
    mode: Optional[str] = None
    revision: Optional[str] = None
    short_revision: Optional[str] = None
    timestamp: Optional[str] = None
    version: Optional[str] = None
    version_hash: Optional[str] = None


class CheckPermissionsResponse(BaseModel):
    allowed: Optional[bool] = None


class CopyMetadataRequest(BaseModel):
    recursive: Optional[bool] = None
    src_dst: List[metadata.SrcDst]


class FileDownloadTokenResponse(BaseModel):
    token: Optional[str] = None


class GetMetadataRequest(BaseModel):
    paths: Optional[List[str]] = None


class MetadataConfigResponse(BaseModel):
    config: Optional[Dict[str, Any]] = None


class MoveMetadataRequest(BaseModel):
    recursive: Optional[bool] = None
    src_dst: List[metadata.SrcDst]


class OpIdResponse(BaseModel):
    id: Optional[str] = "2diK2kCkpgeHAQSNthIZ1JYyPte"
    location: Optional[str] = "/api/v1/operations/2diK2kCkpgeHAQSNthIZ1JYyPte"


class OpsRequest(BaseModel):
    ids: List[str]


class PermissionsConfigResponse(BaseModel):
    config: Optional[Dict[str, Any]] = None


class RemoveMetadataRequest(BaseModel):
    paths: List[str]
    recursive: Optional[bool] = None


class SetMetadataRequest(BaseModel):
    metadata: metadata.DataAssignments


class Status(BaseModel):
    build_info: Optional[BuildInfo] = None
    ready: Optional[bool] = None
    time: Optional[str] = None


class StorageConfigResponse(BaseModel):
    storage: Optional[List[Dict[str, Any]]] = None


class StoragePath(BaseModel):
    path: str
    remote: Optional[str] = "any"


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
