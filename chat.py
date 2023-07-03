import sys
import argparse
from socket import *
import json
import logging
import inspect
import time

name = sys.argv[0].split('.')[0]
logger = logging.getLogger(name)

ADDRESS = 'localhost'
PORT = 7777
CONNECTIONS = 10
BYTES = 1024
TIMEOUT = 1.0
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
    parser_group.add_argument('-n', '--name', default=None, help='Username')
    logger.info(f'Полёт нормальный')

    return parser

class Chat:
    def __init__(self):
        self.parser = create_parser()
    
    @Log()
    def send_data(self, recipient, data):
        recipient.send(json.dumps(data).encode("utf-8"))

    @Log()
    def get_data(self, sender):
        encoded_response = sender.recv(BYTES)
        if isinstance(encoded_response, bytes):
            msg = json.loads(encoded_response.decode("utf-8"))
            if isinstance(msg, dict):
                return msg
            else:
                raise TypeError('Данные должны быть словарем')
        else:
            raise TypeError('Данные должны быть байтами')


    
# class BaseServer(Chat, metaclass = ServerMaker) :
#     @Log()
#     def get_server_socket(self, addr, port):
#         s = socket(AF_INET, SOCK_STREAM)
#         s.bind((addr, port))
#         s.listen(CONNECTIONS)
#         s.settimeout(TIMEOUT)
#         return s

# class BaseClient(Chat):
#     @Log()
#     def get_client_socket(self, addr, port):
#         s = socket(AF_INET, SOCK_STREAM)
#         s.connect((addr, port))
#         return s
    