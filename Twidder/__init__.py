from flask import Flask
app = Flask(__name__)

import Twidder.views  # nopep8

from gevent.pywsgi import WSGIServer  # nopep8

if __name__ == 'Twidder':
    print('running')
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
