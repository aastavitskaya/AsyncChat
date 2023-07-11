import sys
import os
import threading
import time
import binascii
import base64
import hmac
import hashlib
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from client.client_utils import MessageHandlerMixin
from client.gui import welcome
from config.settigs import DEFAULT_PORT, CHECK_TIMEOUT, ENCODING, ITERATIONS
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
        self.keys = None
        self.db = None
        self.public_key = None
        self.decryptor = None
        self.encryptor = None

    @Log()
    def request_public_key(self, username):
        self.send_message(
            self.sock,
            self.create_message(
                action="public_key_request",
                user_id=username,
            ),
        )
        public_key = self.receive_message()
        self.encryptor = PKCS1_OAEP.new(RSA.import_key(public_key))

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
    def authorisation(self, ui):
        password = self.password.encode(ENCODING)
        salt = self.username.encode(ENCODING)
        password_hash = hashlib.pbkdf2_hmac("sha256", password, salt, ITERATIONS)
        password_hash_string = binascii.hexlify(password_hash)
        message = self.create_message(action="login")
        self.send_message(self.sock, message)
        response = self.receive_message()
        if response == "rejected":
            ui.error = f"Sorry, username {self.username} is busy :("
            self.username = None
        else:
            check_hash = hmac.new(
                password_hash_string, response.encode(ENCODING), "sha256"
            )
            digest = check_hash.digest()
            digest_message = {
                "action": "auth",
                "response": HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED,
                "body": binascii.b2a_base64(digest).decode(ENCODING),
            }
            self.send_message(self.sock, self.create_message(**digest_message))
            response = self.receive_message()
            if response == "rejected":
                ui.error = f"Check your credentials :("
                self.username = None

    @Log()
    def registration(self, ui):
        message = {
            "action": "register",
            "password": self.password,
        }
        reg_request = self.create_message(**message)
        self.send_message(self.sock, reg_request)
        reg_response = self.receive_message()
        if reg_response == "accepted":
            ui.error = f"User {self.username} created"
        elif reg_response == "rejected":
            ui.error = f"Sorry, username {self.username} is busy :("
        self.username = None

    @Log()
    def set_username(self, app):
        dialog = welcome.UiDialog()
        dialog.setupUi()
        dialog.error = ""
        while not self.username:
            dialog.input_username(dialog.error)
            app.exec()
            self.username = dialog.lineEdit.text()
            self.password = dialog.lineEdit_2.text()
            if not dialog.new_user:
                self.authorisation(dialog)
                # password = self.password.encode(ENCODING)
                # salt = self.username.encode(ENCODING)
                # password_hash = hashlib.pbkdf2_hmac(
                #     "sha256", password, salt, ITERATIONS
                # )
                # password_hash_string = binascii.hexlify(password_hash)
                # message = self.create_message(action="login")
                # self.send_message(self.sock, message)
                # response = self.receive_message()
                # if response == "rejected":
                #     error = f"Sorry, username {self.username} is busy :("
                #     self.username = None
                # else:
                #     check_hash = hmac.new(
                #         password_hash_string, response.encode(ENCODING), "sha256"
                #     )
                #     digest = check_hash.digest()
                #     digest_message = {
                #         "action": "auth",
                #         "response": HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED,
                #         "body": binascii.b2a_base64(digest).decode(ENCODING),
                #     }
                #     self.send_message(self.sock, self.create_message(**digest_message))
                #     response = self.receive_message()
                #     if response == "rejected":
                #         error = f"Check your credentials :("
                #         self.username = None
            else:
                self.registration(dialog)
                # message = {
                #     "action": "register",
                #     "password": self.password,
                # }
                # reg_request = self.create_message(**message)
                # self.send_message(self.sock, reg_request)
                # reg_response = self.receive_message()
                # if reg_response == "accepted":
                #     error = f"User {self.username} created"
                # elif reg_response == "rejected":
                #     error = f"Sorry, username {self.username} is busy :("
                # self.username = None

        del dialog

    def connect_db(self, db):
        self.db = db

    def load_keys(self):
        key = os.path.join(os.getcwd(), f"rsa_key.{self.username}.key")
        if not os.path.exists(key):
            keys = RSA.generate(2048, os.urandom)
            with open(key, "wb") as f:
                f.write(keys.export_key())
        else:
            with open(key, "rb") as f:
                keys = RSA.import_key(f.read())

        self.keys = keys
        self.decryptor = PKCS1_OAEP.new(keys)
        self.public_key = keys.public_key().export_key()

    @Log()
    def outgoing(self, message):
        message = self.create_message(**message)
        if message.get("body"):
            with self.lock:
                self.db.add_message(
                    message["user_id"],
                    message["body"],
                    message["time"],
                    recieved=False,
                )
            encrypted_body = self.encryptor.encrypt(message["body"].encode(ENCODING))
            message["body"] = base64.b64encode(encrypted_body).decode(ENCODING)
        self.send_message(self.sock, message)
        logger.debug(f"Sent message {message}")

    @Log()
    def incomming(self):
        while True:
            try:
                message = self.receive_message()
                logger.debug(f"Received message {message}")
            except Exception as e:
                logger.error(f"Exception {e} while recieving message {message}")
                pass

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