from flask import Flask, request
from threading import Thread

class Client:
    def __init__(self, key, hook):
        self.key = key
        self.app = Flask(__name__)
        self._initialize_server()
        self.hook = hook
        self.status = {}
    def _initialize_server(self):
        @self.app.route('/start', methods=['POST'])
        def start():
            body = request.get_json()
            task = body['task']
            if body['key'] != self.key:
                print('received invalid key', body['key'], self.key)
                return 'Invalid key', 403
            self.status[task] = self.hook(task)
            return 'OK', 200
        return self.app
    def start_listening(self, host='0.0.0.0', port=4444) -> Thread:
        t = Thread(target=self.app.run, args=(host, port))
        t.daemon = True
        t.start()
        return t