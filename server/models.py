# generated by fastapi-codegen:
#   filename:  openapi.yaml
#   timestamp: 2024-07-18T00:31:27+00:00

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, conint


class Task(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    runner: Optional[str] = None
    creator: Optional[str] = None
    last_update: Optional[datetime] = None
    created_date: Optional[datetime] = None
    queue: Optional[List[str]] = None
    state: Optional[conint(ge=0, le=2)] = None


class User(BaseModel):
    id: Optional[str] = None
    key: Optional[str] = None
    url: Optional[AnyUrl] = None


class TasksPostRequest(BaseModel):
    name: str = ''
    description: Optional[str] = 'No description'


class TasksNamePutRequest(BaseModel):
    data: Optional[str] = None


class UsersNamePostResponse(BaseModel):
    key: Optional[str] = None
