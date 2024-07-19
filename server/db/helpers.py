from random import choice
import datetime

ALPHABET = ''.join(chr(i) for i in range(97, 97+26))+''.join(chr(i) for i in range(65, 65+26))+'0123456789'
KEY_SIZE = 32

class LogicError(Exception): pass
class DuplicationError(LogicError): pass
class CoordinationError(LogicError): pass
class PermissionError(LogicError): pass
class NotFoundError(LogicError): pass

def generate_key(size=KEY_SIZE): # NOT cryptographically secure!
    return ''.join(choice(ALPHABET) for _ in range(size))


def current_time():
    return datetime.datetime.now().isoformat()

def decode(s):
    try: return s.decode('utf-8')
    except: return s
