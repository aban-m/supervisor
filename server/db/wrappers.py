import os, dotenv
import redis
from .helpers import *

dotenv.load_dotenv()
HOST = os.getenv('REDIS_HOST', '127.0.0.1')
PORT = int(os.getenv('REDIS_PORT', 6379))

r = redis.StrictRedis(host=HOST, port=PORT, 
                      db = 0,
                      decode_responses=True, charset='utf-8')

def verify_user(id, key):
    return key and r.hget(f'user:{id}', 'key') == key

def register_user(id, link=''):
    if r.exists(f'user:{id}'):
        raise DuplicationError('User already exists')
    key = generate_key()
    r.hset(f'user:{id}', mapping={'link': link, 'key':key})
    return key

def delete_user(id):
    r.delete(f'user:{id}')   

def get_user_link(id):
    link = r.get(f'users:{id}')
    if not link: raise NotFoundError('User has not supplied link')
    return link


def create_task(id, name, desc='', data=''):
    entry_name = f'task:{name}'
    qentry_name = f'task_queue:{name}'
    if r.exists(entry_name):
        raise DuplicationError('Task already exists.')
    r.hset(entry_name, mapping={
        'desc': desc,
        'data': data,
        'creator': id,
        'runner': '',
        'state': 0,
        'last_updated': '',
        'created_date': current_time()
    })

def delete_task(name):
    r.delete(f'task:{name}')
    r.delete(f'task_queue:{name}')

def get_task(name):
    d = r.hgetall(f'task:{name}').items()
    if not d: return None
    d['queue'] = task_queue(name)
    return d

def search_tasks(s, limit):
    names = [out[5:] for out in r.scan(0, f'task:{s}', limit)[1]]
    tasks = r.mget([f'task:{s}' for s in names])
    queues = r.mget([f'task_queue:{s}' for s in names])
    for task, queue in zip(tasks, queues):
        task['queue'] = queue
    return tasks

def task_queue(name):
    return r.lrange(f'task_queue:{name}', 0, -1)

def task_enqueue(id, name):
    r.lpush(f'task_queue:{name}', id)

def task_peek(name):
    try: return r.lrange(f'task_queue:{name}', -1, -1)[0]
    except IndexError: return None

def task_dequeue(name):
    return r.rpop(f'task_queue:{name}')

def set_task_attr(name, key, val): r.hset(f'task:{name}', key, val)
def get_task_attr(name, key): return r.hget(f'task:{name}', key)

def update_task_data(name, data, append=False):
    entry_name = f'task:{name}'
    if append:
        data = r.hget(entry_name, 'data') + bytes(data, encoding='utf-8')
    r.hset(entry_name, 'data', data)
    r.hset(entry_name, 'last_updated', current_time())

def set_task_runner(id, name):
    set_task_attr(name, 'runner', id)
    set_task_attr(name, 'state', b'2')

def stop_task(id, name):
    set_task_attr(name, 'runner', '')
    set_task_attr(name, 'state', b'0' if task_peek(name) else b'1')

def queue_task(name):
    state = get_task_attr(name, 'state')
    if state != b'2':
        set_task_attr(name, 'state', b'1')

# VALIDATION

def validate_task_run(id, name, strict=False):
    if get_task_attr(name, 'state') == b'2':
        raise CoordinationError('Task is already running.')
    heir = task_peek(name)
    if id != task_peek(name) and (not strict and heir is None):
        raise PermissionError(f'{id} is not next in line.')

def validate_task_delete(id, name, strict=False):
    state, creator = r.hmget(f'task:{name}', ['state', 'creator'])
    if state is None: raise NotFoundError('Task not found.')
    if int(state) == 2: raise PermissionError('Task is running.')
    if creator != id: raise PermissionError(f'{id} is not the creator.')

def validate_task_update(id, name, strict=False):
    if id != get_task_attr(name, 'runner'): raise PermissionError(f'{id} is not the runner.')
    if strict:
        if not r.exists(f'task:{name}'): raise CoordinationError('Task must be running.')
        if get_task_attr(name, 'state')!=b'2': raise CoordinationError('Task must be running.')

def validate_task_stop(id, name, strict=False):
    if id != get_task_attr(name, 'runner'): raise PermissionError(f'{id} is not the runner.')

def validate_task_enqueue(id, name):
    pass

def validate_id(id):
    return 3 < len(id) < 40 and all(c in ALPHABET for c in id)
