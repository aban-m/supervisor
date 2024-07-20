from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, conint


class Credentials(BaseModel):
    id: str
    key: str


class Task(BaseModel):
    name: str
    desc: Optional[str] = ''
    runner: str
    creator: str
    data: Optional[str] = ''
    last_updated: Optional[datetime] = None
    created_date: datetime


class TaskNamePutRequest(BaseModel):
    credentials: Credentials
    data: str

class UserPostRequest(BaseModel):
    id: str
    link: Optional[str] = ''

class TaskPostRequest(BaseModel):
    credentials: Credentials
    name: str
    desc: str = ''
