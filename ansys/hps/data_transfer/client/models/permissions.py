# generated by datamodel-codegen

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ResourceType(Enum):
    Doc = "document"


class RoleType(Enum):
    Reader = "reader"
    Writer = "writer"
    Admin = "admin"


class SubjectType(Enum):
    User = "user"
    Group = "group"


class Resource(BaseModel):
    path: Optional[str] = "my/path/to/data/file.txt"
    type: Optional[ResourceType] = None


class Subject(BaseModel):
    id: Optional[str] = "946991ec-828c-4de4-acbe-962ada8bc441"
    type: Optional[SubjectType] = None


class RoleAssignment(BaseModel):
    resource: Optional[Resource] = None
    role: Optional[RoleType] = None
    subject: Optional[Subject] = None


class RoleQuery(BaseModel):
    resource: Optional[Resource] = None
    role: Optional[RoleType] = None
    subject: Optional[Subject] = None
