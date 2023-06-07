import sys
import os
sys.path.append(os.getcwd)


import unittest
import chat
from server import Server
from client import Client

TEST_ADDR = '127.0.0.1'
TEST_PORT = 7777


class TestChat(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()