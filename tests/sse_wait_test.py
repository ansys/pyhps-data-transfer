# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons who the Software is
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

"""Tests for SSE waiter functionality."""

import os
import tempfile

import pytest

from ansys.hps.data_transfer.client import AsyncDataTransferApi, DataTransferApi
from ansys.hps.data_transfer.client.api.waiter import AsyncSseWaiter, SseWaiter, generate_subject
from ansys.hps.data_transfer.client.models import OperationState, SrcDst, StoragePath


def test_generate_subject():
    """Test that generate_subject creates a unique hex string."""
    subject1 = generate_subject()
    subject2 = generate_subject()
    assert isinstance(subject1, str)
    assert len(subject1) == 32  # UUID4 hex is 32 chars
    assert subject1 != subject2


def _skip_if_sse_unsupported(api):
    """Skip the current test if the connected server does not advertise SSE support."""
    status = api.status()
    features = status.features
    if not features or not features.sse:
        pytest.skip("Server does not advertise SSE support")


async def _skip_if_sse_unsupported_async(api):
    """Skip the current test if the connected server does not advertise SSE support (async)."""
    status = await api.status()
    features = status.features
    if not features or not features.sse:
        pytest.skip("Server does not advertise SSE support")


def test_sse_waiter_with_copy(client, storage_path):
    """Test SSE waiter with a copy operation."""
    api = DataTransferApi(client)
    _skip_if_sse_unsupported(api)

    # Generate subject
    subject = generate_subject()

    # Create test file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for SSE")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        # Start SSE waiter
        with SseWaiter(api.client.session, subject) as waiter:
            # Submit operation with same subject
            ops = [
                SrcDst(
                    src=StoragePath(path=test_file, remote="local"),
                    dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
                )
            ]
            api.copy(ops, subject=subject)

            # Wait for completion via SSE
            final_op = None
            for op in waiter:
                final_op = op
                if waiter.is_terminal:
                    break

        # Verify operation completed
        assert final_op is not None
        assert final_op.state in (OperationState.Succeeded, OperationState.Failed)
    finally:
        os.unlink(test_file)


def test_wait_for_with_sse(client, storage_path):
    """Test wait_for with SSE enabled."""
    api = DataTransferApi(client)
    _skip_if_sse_unsupported(api)
    subject = generate_subject()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for wait_for SSE")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        ops = [
            SrcDst(
                src=StoragePath(path=test_file, remote="local"),
                dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
            )
        ]
        result = api.copy(ops, subject=subject)

        # Wait with SSE, using the same subject as the operation submission
        final_ops = api.wait_for(result.id, use_sse=True, subject=subject)
        assert final_ops is not None
        assert len(final_ops) > 0
        assert final_ops[0].state in (OperationState.Succeeded, OperationState.Failed)
    finally:
        os.unlink(test_file)


def test_wait_for_without_sse(client, storage_path):
    """Test wait_for with SSE disabled (polling fallback)."""
    api = DataTransferApi(client)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for polling")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        ops = [
            SrcDst(
                src=StoragePath(path=test_file, remote="local"),
                dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
            )
        ]
        result = api.copy(ops)

        # Wait with polling
        final_ops = api.wait_for(result.id, use_sse=False)
        assert final_ops is not None
        assert len(final_ops) > 0
        assert final_ops[0].state in (OperationState.Succeeded, OperationState.Failed)
    finally:
        os.unlink(test_file)


def test_user_provided_subject(client, storage_path):
    """Test that user-provided subject is used."""
    api = DataTransferApi(client)
    _skip_if_sse_unsupported(api)

    custom_subject = "my-custom-subject-123"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for custom subject")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        ops = [
            SrcDst(
                src=StoragePath(path=test_file, remote="local"),
                dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
            )
        ]
        result = api.copy(ops, subject=custom_subject)

        # Wait with SSE and custom subject
        final_ops = api.wait_for(result.id, use_sse=True, subject=custom_subject)
        assert final_ops is not None
        assert len(final_ops) > 0
    finally:
        os.unlink(test_file)


@pytest.mark.asyncio
async def test_async_sse_waiter(async_client, storage_path):
    """Test async SSE waiter with a copy operation."""
    api = AsyncDataTransferApi(async_client)
    await _skip_if_sse_unsupported_async(api)

    subject = generate_subject()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for async SSE")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        async with AsyncSseWaiter(api.client.session, subject) as waiter:
            ops = [
                SrcDst(
                    src=StoragePath(path=test_file, remote="local"),
                    dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
                )
            ]
            await api.copy(ops, subject=subject)

            final_op = None
            async for op in waiter:
                final_op = op
                if waiter.is_terminal:
                    break

        assert final_op is not None
        assert final_op.state in (OperationState.Succeeded, OperationState.Failed)
    finally:
        os.unlink(test_file)


@pytest.mark.asyncio
async def test_async_wait_for_with_sse(async_client, storage_path):
    """Test async wait_for with SSE enabled."""
    api = AsyncDataTransferApi(async_client)
    await _skip_if_sse_unsupported_async(api)
    subject = generate_subject()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for async wait_for SSE")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        ops = [
            SrcDst(
                src=StoragePath(path=test_file, remote="local"),
                dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
            )
        ]
        result = await api.copy(ops, subject=subject)

        final_ops = await api.wait_for(result.id, use_sse=True, subject=subject)
        assert final_ops is not None
        assert len(final_ops) > 0
        assert final_ops[0].state in (OperationState.Succeeded, OperationState.Failed)
    finally:
        os.unlink(test_file)


@pytest.mark.asyncio
async def test_async_wait_for_without_sse(async_client, storage_path):
    """Test async wait_for with SSE disabled (polling fallback)."""
    api = AsyncDataTransferApi(async_client)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test data for async polling")
        test_file = f.name
    test_file_name = os.path.basename(test_file)

    try:
        ops = [
            SrcDst(
                src=StoragePath(path=test_file, remote="local"),
                dst=StoragePath(path=f"{storage_path}/{test_file_name}"),
            )
        ]
        result = await api.copy(ops)

        final_ops = await api.wait_for(result.id, use_sse=False)
        assert final_ops is not None
        assert len(final_ops) > 0
        assert final_ops[0].state in (OperationState.Succeeded, OperationState.Failed)
    finally:
        os.unlink(test_file)
