import os
import sys
import json
import time
import unittest

sys.path.append(os.getcwd())

from config.settigs import ERRORS, ENCODING, MAX_PACKAGE_LENGTH
from config.utils import Chat

TEST_IP = "127.0.0.1"


class TestSocket:
    def __init__(self, message):
        self.encoded_message = json.dumps(message).encode(ENCODING)

    def recv(self, package_length=MAX_PACKAGE_LENGTH):
        return self.encoded_message

    def send(self, message):
        self.sent = json.loads(message.decode(ENCODING))


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.time = time.time()
        self.message = {"action": "msg", "time": self.time}
        self.chat = Chat()
        self.test_sock = TestSocket(self.message)

    def test_get_errors(self):
        self.assertIn(self.chat.get_error, ERRORS)

    def test_template_message(self):
        self.assertEqual(self.chat.template_message(time=self.time), self.message)

    def test_template_message_kwargs(self):
        kwargs = {"test_key": "test_value"}
        self.assertEqual(self.chat.template_message(**kwargs)["test_key"], "test_value")

    def test_get_message(self):
        test_sock = TestSocket(self.message)
        message = self.chat.get_message(test_sock)
        self.assertEqual(message, self.message)

    def test_send_message(self):
        self.chat.send_message(self.test_sock, self.message)
        self.assertEqual(self.test_sock.sent, self.message)


if __name__ == "__main__":
    unittest.main()
