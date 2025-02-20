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
    Any = "any"


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
