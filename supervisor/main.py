from __future__ import annotations

from typing import List, Optional
from functools import wraps
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, HTTPException

from .models import Credentials, Task, TaskNamePutRequest, TaskPostRequest, UserPostRequest
from .db import wrappers, helpers
from .daemon import chronos


@asynccontextmanager
async def lifespan(app : FastAPI):
    # launch daemon on startup
    asyncio.create_task(chronos.watch_forever())
    yield
    print('Shutting down...')

app = FastAPI(
    title='Supervisor Server API',
    version='0.0.1',
    description='The server-side of the Supervisor API',
    lifespan=lifespan
)

def requires_validation(func):
    @wraps(func)
    def myfunc(body, *args, **kwargs):
        creds = body if isinstance(body, Credentials) else body.credentials
        if not wrappers.verify_user(creds.id, creds.key):
            raise HTTPException(401, 'Invalid credentials')
        return func(body, *args, **kwargs)
    return myfunc


@app.get('/task', response_model=List[Task])
def search_tasks(pattern: Optional[str] = '*', limit: Optional[int] = 10) -> List[Task]:
    return [Task(**d) for d in wrappers.search_tasks(pattern, limit)]


@app.post('/task', response_model=None)
@requires_validation
def create_task(body: TaskPostRequest) -> None:
    try: wrappers.create_task(body.credentials.id, body.name, body.desc)
    except helpers.DuplicationError as e: raise HTTPException(409, str(e))

@app.delete('/task/{name}', response_model=None)
@requires_validation
def delete_task(body : Credentials = ..., name : str = ...) -> None:
    # validate then delete
    try: wrappers.validate_task_delete(body.id, name)
    except helpers.NotFoundError as e: raise HTTPException(404, str(e))
    except helpers.PermissionError as e: raise HTTPException(403, str(e))
    wrappers.delete_task(name)


@app.put('/task/{name}', response_model=None)
@requires_validation
def update_task(body: TaskNamePutRequest = ..., name: str = ...) -> None:
    # validate then update
    try: wrappers.validate_task_update(body.credentials.id, name)
    except helpers.NotFoundError: raise HTTPException(404, 'Task not found')
    except helpers.PermissionError: raise HTTPException(403, 'Permission denied')
    wrappers.update_task_data(name, body.data)


@app.get('/task/{name}', response_model=Task)
def get_task(name: str) -> Task:
    return Task(**wrappers.get_task(name))


@app.delete('/task/{name}/queue', response_model=None)
@requires_validation
def dequeue(body: Credentials = ..., name: str = ...) -> None:
    raise HTTPException(500, 'Not implemented')


@app.put('/task/{name}/queue', response_model=None)
@requires_validation
def enqueue(body: Credentials = ..., name: str = ...) -> None:
    # validate then enqueue
    try: wrappers.validate_task_enqueue(body.id, name)
    except helpers.NotFoundError: raise HTTPException(404, 'Task not found')
    except helpers.PermissionError: raise HTTPException(403, 'Permission denied')
    wrappers.task_enqueue(body.id, name)


@app.get('/user/{id}', response_model=str)
def get_user_link(id: str) -> str:
    out = wrappers.get_user_link(str)
    if not out: raise HTTPException(404, 'User not found')
    return out

@app.post('/user', response_model=str)
def register_user(body: UserPostRequest) -> str:
    try: key = wrappers.register_user(body.id, body.link)
    except helpers.DuplicationError as e: raise HTTPException(409, str(e))
    return key

@app.post('/task/{name}/maintain', response_model=None)
@requires_validation
def maintain_task(name: str) -> None:
    runner = wrappers.get_task_attr(name, 'runner')
    if not runner: raise HTTPException(404, 'Task not found.')
    if runner != name: raise HTTPException(403, 'You are not running the task.')
    wrappers.maintain_tasks(name, chronos.MAINTAIN_PERIOD)

@app.post('/task/{name}/run', response_model=None)
@requires_validation
def start_task(body : Credentials, name: str) -> None:
    try: wrappers.validate_task_run(body.id, name)
    except helpers.PermissionError as e: raise HTTPException(403, str(e))
    except helpers.LogicError as e: raise HTTPException(500, str(e))
    wrappers.set_task_runner(body.id, name)
    wrappers.task_dequeue(name) 
    wrappers.maintain_tasks(name, chronos.MAINTAIN_PERIOD)

@app.delete('/task/{name}/run', response_model=None)
@requires_validation
def stop_task(body : Credentials, name: str) -> None:
    try: wrappers.validate_task_update(body.id, name) # works just as well 
    except helpers.NotFoundError as e: raise HTTPException(404, str(e))
    except helpers.PermissionError as e: raise HTTPException(403, str(e))
    wrappers.stop_task(name)
