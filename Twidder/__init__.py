from flask import Flask
app = Flask(__name__)

import Twidder.views  # nopep8

from gevent.pywsgi import WSGIServer  # nopep8
from geventwebsocket.handler import WebSocketHandler  # nopep8

if __name__ == 'Twidder':
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
