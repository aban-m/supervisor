# generated by fastapi-codegen:
#   filename:  db\openapi.yaml
#   timestamp: 2024-07-19T00:39:22+00:00

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


class Credentials(BaseModel):
    id: Optional[str] = None
    key: Optional[str] = None


class TasksPostRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credentials: Optional[Credentials] = None


class TasksNamePutRequest(BaseModel):
    data: Optional[str] = None
    credentials: Optional[Credentials] = None


class UsersNamePostRequest(BaseModel):
    link: Optional[str] = None


class UsersNamePostResponse(BaseModel):
    key: Optional[str] = None
