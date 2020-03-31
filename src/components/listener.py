from http.server import BaseHTTPRequestHandler
from json import dumps, loads

from src.components.cleaner import Cleaner
from src.components.controller import Controller
from src.resources.children import Children
from src.resources.redis import Redis


class Listener(BaseHTTPRequestHandler):
    def __init__(self, controller: Controller, cleaner: Cleaner, *args):
        self.controller = controller
        self.cleaner = cleaner
        super().__init__(*args)

    def do_POST(self):
        observed = loads(self.rfile.read(int(self.headers.get('Content-Length'))))
        redis, children = Redis(observed['parent']), Children(observed['children'])
        desired = self.controller.sync(redis, children)
        desired = self.cleaner.clean(desired)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(dumps(desired).encode('utf-8'))
