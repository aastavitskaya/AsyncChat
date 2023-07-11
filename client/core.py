import sys
import threading
import time
from socket import AF_INET, SOCK_STREAM, socket

from client.client_utils import MessageHandlerMixin
from client.gui import welcome
from config.settigs import DEFAULT_PORT, CHECK_TIMEOUT
from config.utils import BaseVerifier, Chat
from log.settings.client_log_config import logger
from log.settings.decor_log_config import Log


class ClientVerifier(BaseVerifier):
    def __init__(cls, name, bases, namespaces):
        super().__init__(name, bases, namespaces)

        for attr in namespaces.values():
            if isinstance(attr, socket):
                raise TypeError("Socket shouldn't be created at class level")

        params = cls.attrs[f"_{name}_attrs"]
        if "accept" in params or "listen" in params:
            raise TypeError("Accept or listen methods are not allowed")


class Client(Chat, MessageHandlerMixin, metaclass=ClientVerifier):
    def __init__(self):
        self.lock = threading.Lock()
        self.username = None

    @Log()
    def create_message(self, **kwargs):
        logger.info(f"Creating message from user {self.username}")
        return self.template_message(user_login=self.username, **kwargs)

    @Log()
    def presence(self):
        logger.info(f"Creating precense message")
        return self.create_message(action="presence")

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = int(params[2]) if len(params) > 2 else DEFAULT_PORT
        address = params[1]
        logger.info(f"Address: {address} and port: {port} from CLI")
        return address, port

    @Log()
    def connect_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        address, port = self.parse_params
        sock.connect((address, port))
        logger.info(f"Connection to server {address}:{port} was succefully created")
        return sock

    @Log()
    def run(self):
        try:
            self.sock = self.connect_socket()
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)

    @Log()
    def receive_message(self):
        try:
            message = self.get_message(self.sock)
        except Exception:
            logger.critical("Fatal error by receiving message")
            sys.exit(1)
        else:
            logger.info(f"Received message {message}")
            return self.parse_message(message)

    @Log()
    def set_username(self, app):
        dialog = welcome.UiDialog()
        dialog.setupUi()
        error = ""
        while not self.username:
            dialog.input_username(error)
            app.exec()
            self.username = dialog.lineEdit.text()
            message = self.create_message(action="login")
            self.send_message(self.sock, message)
            if self.receive_message() == "rejected":
                error = f"Sorry, username {self.username} is busy :("
                self.username = None

    def connect_db(self, db):
        self.db = db
        # self.send_message(self.sock, self.create_message(action="get_users"))

    @Log()
    def outgoing(self, message):
        if isinstance(message, dict):
            message = self.create_message(**message)
            if message.get("body"):
                with self.lock:
                    self.db.add_message(
                        message["user_id"],
                        message["body"],
                        message["time"],
                        recieved=False,
                    )
            self.send_message(self.sock, message)
        elif message.startswith("/"):
            context = {}
            message = message[1:]
            if message in ("get_contacts", "get_users"):
                context["action"] = message
            elif message in ("add_contact", "del_contact"):
                context["action"] = message
                context["user_id"] = input("Enter username of target: ")
            if context:
                self.send_message(self.sock, self.create_message(**context))
        else:
            pass

    @Log()
    def incomming(self):
        while message := self.receive_message():
            print(message)

    @Log()
    def main_loop(self):
        transmitter = threading.Thread(target=self.outgoing)
        transmitter.daemon = True
        transmitter.start()

        receiver = threading.Thread(target=self.incomming)
        receiver.daemon = True
        receiver.start()

        while True:
            time.sleep(CHECK_TIMEOUT)
            if transmitter.is_alive() and receiver.is_alive():
                continue
            break
