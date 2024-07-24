from .controllers import *

from flask import Flask, request
from configparser import ConfigParser

# read "key" from config.ini
config = ConfigParser()
config.read('config.ini')
key = config['DEFAULT']['key']

app = Flask(__name__)

# in: key, task name
@app.route('/start', methods=['POST'])
def start():
    body = request.get_json()
    task = body['task']
    if body['key'] != key:
        return 'Invalid key', 403
    start_task(task)
    return 'OK', 200