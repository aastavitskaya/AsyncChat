import sys
import argparse
from socket import *
import json
import logging

name = sys.argv[0].split('.')[0]
logger = logging.getLogger(name)

ADDRESS = 'localhost'
PORT = 7777
CONNECTIONS = 10
BYTES = 1024

def create_parser():
    parser = argparse.ArgumentParser(
        description='JSON instant messaging'
    )

    parser_group = parser.add_argument_group(title='Parameters')
    parser_group.add_argument('-a', '--addr', default=ADDRESS, help='IP address')
    parser_group.add_argument('-p', '--port', type=int, default=PORT, help='TCP port')
    logger.info(f'Что же это такое?')

    return parser

class Chat:
    def __init__(self):
        self.parser = create_parser()

    def send_data(self, recipient, data):
        recipient.send(json.dumps(data).encode("utf-8"))

    def get_data(self, sender, bythes_length=BYTES):
        return json.loads(sender.recv(bythes_length).decode("utf-8"))


class BaseServer(Chat):
    def get_server_socket(self, addr, port):
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((addr, port))
        s.listen(CONNECTIONS)
        return s

class BaseClient(Chat):
    def get_client_socket(self, addr, port):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((addr, port))
        return s
