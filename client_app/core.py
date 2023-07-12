"""
Модуль с основным классом клиентского приложения.
"""

import sys
import os
import threading
import binascii
import base64
import hmac
import hashlib
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from client_app.client_utils import MessageHandlerMixin
from client_app.gui import welcome
from config.settigs import DEFAULT_PORT, ENCODING, ITERATIONS
from config.utils import BaseVerifier, Chat
from log.settings.client_log_config import logger
from log.settings.decor_log_config import Log


class ClientVerifier(BaseVerifier):
    """
    Метакласс валидатор, проверяет, что атрибут со ссылкой на сокет не создаётся
    на уровне класса, а также что сокет не использует методы listen и accept.
    """

    def __init__(cls, name, bases, namespaces):
        """
        Магический метод возвращающий объект класса BaseVerifier
        :name: (str) имя класса подлежащего валидации
        :bases: (list) список классов родителей
        :namespase: (dict) словарь атрибутов создаваемого класса
        """
        super().__init__(name, bases, namespaces)

        for attr in namespaces.values():
            if isinstance(attr, socket):
                raise TypeError("Socket shouldn't be created at class level")

        params = cls.attrs[f"_{name}_attrs"]
        if "accept" in params or "listen" in params:
            raise TypeError("Accept or listen methods are not allowed")


class Client(Chat, MessageHandlerMixin, metaclass=ClientVerifier):
    """
    Основной класс клиентского приложения, отвечает за работу с сокетами
    и обработку входящих / исходящих сообщений.
    """

    def __init__(self):
        """
        Метод, инициирующий экземпляр клиентского приложения.
        :lock: (threading.Lock) блокировка для работы с базой данных.
        :sock_lock: (threading.Lock) блокировка для работы с сокетом
        :username: (str_имя пользователя клиентского приложения.
        :keys: (Crypto.PublicKey.RSA) ключи шифрования, для генерации публичного ключа
        и расшифровки входящих сообщений
        :public_key: (str) публичный ключ корреспондента для шифрования исходящих сообщений
        :decryptor: (Crypto.Cipher.PKCS1_OAEP) объект - дешифровщик для расшивровки входящих
        :encryptor: (Crypto.Cipher.PKCS1_OAEP) объект - шифровщик для шифрования исходящих
        :
        """
        self.lock = threading.Lock()
        self.sock_lock = threading.Lock()
        self.username = None
        self.keys = None
        self.db = None
        self.public_key = None
        self.decryptor = None
        self.encryptor = None

    @Log()
    def request_public_key(self, username):
        """
        Метод отправляет запрос корреспонденту на получение его публичного ключа.
        Полученный в ответе ключ сохраняет в объект-шифровщик.
        :username: (str) имя пользователя корреспондента.
        """
        with self.sock_lock:
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
        """
        Метод создающий сообщение из переданных ключевых аргументов.
        :return: (dict) возвращает словарь сообщение.
        """
        logger.info(f"Creating message from user {self.username}")
        return self.template_message(user_login=self.username, **kwargs)

    @Log()
    def presence(self):
        """
        Метод создающий сообщение о присутствии по протоколу JIM/
        :return: (dict) возвращает словарь сообщение, где action == presence
        """
        logger.info(f"Creating precense message")
        return self.create_message(action="presence")

    @property
    @Log()
    def parse_params(self):
        """
        Метод разбирает параметры командной строки и выбирает из них
        ip адрес и порт для подключения к серверу, если порт не задан,
        использует порт, заданный по умолчанию.
        :return: (tuple(str, int))
        """
        params = sys.argv
        port = int(params[2]) if len(params) > 2 else DEFAULT_PORT
        address = params[1]
        logger.info(f"Address: {address} and port: {port} from CLI")
        return address, port

    @Log()
    def connect_socket(self):
        """
        Метод создаёт объект сокета и осуществляет подключение к серверу
        по переданным через командную строку параметрам.
        :return: (socket.socket) возвращает полученный объект сокета.
        """
        sock = socket(AF_INET, SOCK_STREAM)
        address, port = self.parse_params
        sock.connect((address, port))
        logger.info(f"Connection to server {address}:{port} was succefully created")
        return sock

    @Log()
    def run(self):
        """
        Метод осуществляет обработку исключений при попытке подключения к серверу.
        """
        try:
            self.sock = self.connect_socket()
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)

    @Log()
    def receive_message(self):
        """
        Метод осуществляет прием сообщений поступающих из сокета и передачу их на обработку
        :return: (str) возвращает строку, сформированную из тела сообщения.
        """
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
        """
        Метод осуществляет авторизацию пользователя на сервере через
        графический интерфейс.
        :ui: (PyQt6.QtWidgets.QDialog): диалоговое окно.
        """
        password = self.password.encode(ENCODING)
        salt = self.username.encode(ENCODING)
        password_hash = hashlib.pbkdf2_hmac("sha256", password, salt, ITERATIONS)
        password_hash_string = binascii.hexlify(password_hash)
        message = self.create_message(action="login")
        with self.sock_lock:
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
            with self.sock_lock:
                self.send_message(self.sock, self.create_message(**digest_message))
                response = self.receive_message()
            if response == "rejected":
                ui.error = f"Check your credentials :("
                self.username = None

    @Log()
    def registration(self, ui):
        """
        Метод осуществляет регистрацию пользователя на сервере через
        графический интерфейс.
        :ui: (PyQt6.QtWidgets.QDialog): диалоговое окно.
        """
        message = {
            "action": "register",
            "password": self.password,
        }
        reg_request = self.create_message(**message)
        with self.sock_lock:
            self.send_message(self.sock, reg_request)
            reg_response = self.receive_message()
        if reg_response == "accepted":
            ui.error = f"User {self.username} created"
        elif reg_response == "rejected":
            ui.error = f"Sorry, username {self.username} is busy :("
        self.username = None

    @Log()
    def set_username(self, app):
        """
        Метод осуществляющий первичный запрос подключения к серверу
        с целью регистрации или авторизации, используя графический интерфейс.
        :app: (PyQt6.QtWidgets.QApplication) графический интерфейс приложения.
        """
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
            else:
                self.registration(dialog)

        del dialog

    def connect_db(self, db):
        """
        Метод осуществляет подключение экземпляра базы данных
        к клиентскому приложению.
        :db: (ClientDBase) база данных
        """
        self.db = db

    def load_keys(self):
        """
        Метод считывает ключи шифрования из файла либо создает новые, если файл не существует.
        Создает и сохраняет публичный ключ в атрибутах приложения.
        Помещает ключи в объект-дешифровщик.
        """
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
        """
        Метод, передающий исходящие сообщения через сокет. Предварительно
        осуществляет сохранение исходящего сообщения в базу и шифрование.
        :message: (dict) объект исходящего сообщения - словарь.
        """
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
        """
        Метод осуществляет обработку исключений, возникающих при получении
        входящих сообщений из сокета.
        """
        while True:
            try:
                message = self.receive_message()
                logger.debug(f"Received message {message}")
            except Exception as e:
                logger.error(f"Exception {e} while recieving message {message}")
                pass
