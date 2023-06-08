import sys
import os
sys.path.append(os.getcwd)

import unittest
import socket
from server import Server

TEST_ADDR = '127.0.0.1'
TEST_PORT = 7777


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.sock = self.server.get_server_socket(TEST_ADDR, TEST_PORT)

    def tearDown(self):
        self.sock.close()
    
    def test_socket(self):
        self.assertIsInstance(self.sock, socket.socket)

    
if __name__ == '__main__':
    unittest.main()