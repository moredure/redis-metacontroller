from functools import partial
from http.server import ThreadingHTTPServer
from os import environ
from signal import signal, SIGTERM, SIGINT
from threading import Thread

from src.components.checker import Checker
from src.components.cleaner import Cleaner
from src.components.controller import Controller
from src.components.creator import Creator
from src.components.listener import Listener
from src.components.resolver import Resolver
from src.components.suicide import Suicide
from src.tools.config import Config

if __name__ == '__main__':
    config = Config(environ)
    creator = Creator(config)
    checker, resolver = Checker(), Resolver(creator)
    controller, cleaner = Controller(checker, resolver), Cleaner()
    ListenerWithController = partial(Listener, controller, cleaner)
    server = ThreadingHTTPServer(config.address, ListenerWithController)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
    suicide = Suicide(server)
    signal(SIGTERM, suicide.die)
    signal(SIGINT, suicide.die)
    server_thread.join()
