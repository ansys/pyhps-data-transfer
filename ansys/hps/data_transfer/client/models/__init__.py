# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2024-07-19T08:19:49+00:00

from __future__ import annotations

from pydantic import BaseModel, Field


class FieldDataRemotePathPostRequest(BaseModel):
    file: bytes = Field(..., description='File')
