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

"""This module provides the core API functionality for interacting with the
Ansys HPS Data Transfer Client. It includes methods and utilities for performing
data transfer operations, managing resources, and handling client interactions.
"""

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
    """Class for Data transfer API.

    Parameters
    ----------
    client: Client
        Client object.
    """

    def __init__(self, client: Client):
        self.dump_mode = "json"
        self.client = client

    @retry()
    def status(self, wait=False, sleep=5, jitter=True, timeout: float | None = 20.0):
        """Status of worker binary."""

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
        """Get a list of operations.

        Parameters
        ----------
        ids: List[str]
            List of ids.
        """
        return self._operations(ids)

    def storages(self):
        """Get types of storages available on the storage backend."""
        url = "/storage"
        resp = self.client.session.get(url)
        json = resp.json()
        return StorageConfigResponse(**json).storage

    def copy(self, operations: List[SrcDst]):
        """Get API response for copying a list of files.

        Parameters
        ----------
        operations: List[SrcDst]
        """
        return self._exec_operation_req("copy", operations)

    def exists(self, operations: List[StoragePath]):
        """Check if a path exists.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("exists", operations)

    def list(self, operations: List[StoragePath]):
        """List files in a path.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("list", operations)

    def mkdir(self, operations: List[StoragePath]):
        """Create a dir.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("mkdir", operations)

    def move(self, operations: List[SrcDst]):
        """Move a file on the backend storage.

        Parameters
        ----------
        operations: List[SrcDst]
        """
        return self._exec_operation_req("move", operations)

    def remove(self, operations: List[StoragePath]):
        """Delete a file.

        Parameters
        ----------
        operations: List[StoragePath]
        """
        return self._exec_operation_req("remove", operations)

    def rmdir(self, operations: List[StoragePath]):
        """Delete a dir.

        Parameters
        ----------
        operations: List[StoragePath]
        """
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
        """Checks permissions of a path (including parent directory) using a list of RoleAssignment objects.

        Parameters
        ----------
        permissions: List[RoleAssignment]
        """
        url = "/permissions:check"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return CheckPermissionsResponse(**json)

    @retry()
    def get_permissions(self, permissions: List[RoleQuery]):
        """Return permissions of a file from a list of RoleQuery objects.

        Parameters
        ----------
        permissions: List[RoleQuery]
        """
        url = "/permissions:get"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return GetPermissionsResponse(**json)

    @retry()
    def remove_permissions(self, permissions: List[RoleAssignment]):
        """Remove permissions using a list of RoleAssignment objects.

        Parameters
        ----------
        permissions: List[RoleAssignment]
        """
        url = "/permissions:remove"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)
        return None

    @retry()
    def set_permissions(self, permissions: List[RoleAssignment]):
        """Set permissions using a list of RoleAssignment objects.

        Parameters
        ----------
        permissions: List[RoleAssignment]
        """
        url = "/permissions:set"
        payload = {"permissions": [permission.model_dump(mode=self.dump_mode) for permission in permissions]}
        self.client.session.post(url, json=payload)
        return None

    @retry()
    def get_metadata(self, paths: List[str | StoragePath]):
        """Get metadata of a path on backend storage.

        Parameters
        ----------
        paths: List[str | StoragePath]
        """
        url = "/metadata:get"
        paths = [p if isinstance(p, str) else p.path for p in paths]
        payload = {"paths": paths}
        resp = self.client.session.post(url, json=payload)
        json = resp.json()
        return OpIdResponse(**json)

    @retry()
    def set_metadata(self, asgs: Dict[str | StoragePath, DataAssignment]):
        """Setting metadata for a path on backend storage.

        Parameters
        ----------
        asgs: Dict[str | StoragePath, DataAssignment]
            List of paths with key of type string or StoragePath and value of DataAssignment
        """
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
        raise_on_error: bool = False,
    ):
        """Wait for operations to complete."""
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
                so_far = hf.format_timespan(time.time() - start)
                log.debug(f"Waiting for {len(operation_ids)} operations to complete, {so_far} so far")
                if self.client.binary_config.debug:
                    for op in ops:
                        fields = [
                            f"id={op.id}",
                            f"state={op.state}",
                            f"start={op.started_at}",
                            f"succeeded_on={op.succeeded_on}",
                        ]
                        if op.progress > 0:
                            fields.append(f"progress={op.progress:.3f}")
                        log.debug(f"- Operation '{op.description}' {' '.join(fields)}")
                if all(op.state in [OperationState.Succeeded, OperationState.Failed] for op in ops):
                    break
            except Exception as e:
                log.debug(f"Error getting operations: {e}")
                if raise_on_error:
                    raise

            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Timeout waiting for operations to complete")

            # TODO: Adjust based on transfer speed and file size
            duration = get_expo_backoff(interval, attempts=attempt, cap=cap, jitter=True)
            if self.client.binary_config.debug:
                log.debug(f"Next check in {hf.format_timespan(duration)} ...")
            time.sleep(duration)

        duration = hf.format_timespan(time.time() - start)
        log.debug(f"Operations completed after {duration}: {op_str}")
        return ops
