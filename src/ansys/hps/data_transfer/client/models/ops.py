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

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class OperationState(Enum):
    Unknown = "unknown"
    Queued = "queued"
    Running = "running"
    Succeeded = "succeeded"
    Failed = "failed"


class Operation(BaseModel):
    children: Optional[List[str]] = None
    description: Optional[str] = None
    ended_at: Optional[str] = None
    error: Optional[str] = None
    id: Optional[str] = None
    messages: Optional[List[str]] = None
    progress: Optional[float] = None
    progress_current: Optional[int] = None
    progress_total: Optional[int] = None
    queued_at: Optional[str] = None
    result: Optional[Any] = None
    started_at: Optional[str] = None
    state: Optional[OperationState] = None
    succeeded_on: Optional[List[str]] = Field(None, description="Remotes that the operation succeeded on")
    user_id: Optional[str] = None
