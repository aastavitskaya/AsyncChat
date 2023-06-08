import sys
import os
import socket
from unittest.mock import patch

sys.path.append(os.getcwd)


import unittest
from server import Server
from client import Client

TEST_ADDR = '127.0.0.1'
TEST_PORT = 7777


class TestChat(unittest.TestCase):

    @patch("sys.argv", ["client.py", "-a", TEST_ADDR, "-p", str(TEST_PORT)])
    def setUp(self):
        @patch("sys.argv", ["", TEST_ADDR])
        def _connect_socket(client):
            return client.connect_socket()
        
        self.server = Server()
        self.client = Client()

        self.server.create_socket()


    def tearDown(self):
        pass

    @patch("sys.argv", ["client.py", "-a", TEST_ADDR, "-p", str(TEST_PORT)])
    def test_create_socket(self):
        self.client.create_socket()
        isinstance(self.client.socket, socket.socket)


if __name__ == '__main__':
    unittest.main()