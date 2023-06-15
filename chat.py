import sys
import argparse
from socket import *
import json
import logging
import inspect


name = sys.argv[0].split('.')[0]
logger = logging.getLogger(name)

ADDRESS = 'localhost'
PORT = 7777
CONNECTIONS = 10
BYTES = 1024

class Log:
    def __call__(self, func):
        def wrap(*args, **kwargs):
            wrapped_args = (
                args[1:]
                if args and issubclass(args[0].__class__, (Chat, type))
                else args
            )
            rez = func(*args, **kwargs)
            logger.info(
                f'Function {func.__name__} with parameters {*wrapped_args, *kwargs}'
                f'was called from function {inspect.stack()[1][3]}', stacklevel=2)
            return rez
    
        return wrap

@Log()
def create_parser():
    parser = argparse.ArgumentParser(
        description='JSON instant messaging'
    )

    parser_group = parser.add_argument_group(title='Parameters')
    parser_group.add_argument('-a', '--addr', default=ADDRESS, help='IP address')
    parser_group.add_argument('-p', '--port', type=int, default=PORT, help='TCP port')
    logger.info(f'Полёт нормальный')

    return parser

class Chat:
    def __init__(self):
        self.parser = create_parser()
    
    @Log()
    def send_data(self, recipient, data):
        recipient.send(json.dumps(data).encode("utf-8"))

    @Log()
    def get_data(self, sender, bythes_length=BYTES):
        return json.loads(sender.recv(bythes_length).decode("utf-8"))


class BaseServer(Chat):
    @Log()
    def get_server_socket(self, addr, port):
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((addr, port))
        s.listen(CONNECTIONS)
        return s

class BaseClient(Chat):
    @Log()
    def get_client_socket(self, addr, port):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((addr, port))
        return s
    