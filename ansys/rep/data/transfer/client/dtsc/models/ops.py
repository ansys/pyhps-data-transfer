# generated by datamodel-codegen:
#   filename:  openapi.yaml
#   timestamp: 2024-05-06T15:33:03+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OperationState(Enum):
    Unknown = "unknown"
    Queued = "queued"
    Running = "running"
    Succeeded = "succeeded"
    Failed = "failed"


class Operation(BaseModel):
    children: Optional[List[str]] = None
    description: Optional[str] = None
    error: Optional[str] = None
    id: Optional[str] = None
    messages: Optional[List[str]] = None
    progress: Optional[float] = None
    result: Optional[Dict[str, Any] | bool] = None
    state: Optional[OperationState] = None
