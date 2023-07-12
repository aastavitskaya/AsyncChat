import select
import sys
from queue import Queue
import threading
from http import HTTPStatus
from collections import deque
from socket import AF_INET, SOCK_STREAM, socket

from config.settigs import DEFAULT_PORT, MAX_CONNECTIONS, TIMEOUT
from config.utils import Chat, BaseVerifier
from server_app.server_utils import Users, ExchangeMessageMixin, NamedPort
from server_app.exceptions import PortError
from log.settings.decor_log_config import Log
from log.settings.server_log_config import logger


class ServerVerifier(BaseVerifier):
    def __init__(cls, name, bases, namespaces):
        super().__init__(name, bases, namespaces)

        if "connect" in cls.attrs[f"_{name}_attrs"]:
            raise TypeError("Connect method is not allowed")


class Server(Chat, ExchangeMessageMixin, metaclass=ServerVerifier):
    port = NamedPort("server_port", DEFAULT_PORT)

    def __init__(self, db):
        self.users = Users()
        self.queue = Queue()
        self.lock = threading.Lock()
        self.messages = deque()
        self.dispatcher = select.poll()
        self.db = db

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = int(params[params.index("-p") + 1]) if "-p" in params else ""
        address = params[params.index("-a") + 1] if "-a" in params else ""
        logger.info(
            f"Address: {address if address else '0.0.0.0'} "
            f"and port: {port if port else 'by default'} from CLI"
        )
        return address, port

    @Log()
    def init_socket(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        address, self.port = self.parse_params
        self.sock.bind((address, self.port))
        self.sock.settimeout(TIMEOUT)
        self.sock.listen(MAX_CONNECTIONS)
        logger.info(
            f"Socket was succefully created with max average of connections: {MAX_CONNECTIONS}"
        )

    @Log()
    def disconnect_client(self, client):
        logger.info(f"Client {client} disconnected")
        self.dispatcher.unregister(self.users.sockets[client])
        if self.users.get_username(client):
            self.db.deactivate_client(self.users.get_username(client))
        self.users.sockets[client].close()
        self.users.delete_user(client)

    @Log()
    def check_messages(self, events):
        for client, event in events:
            if event & select.POLLIN:
                try:
                    message = self.get_message(self.users.sockets[client])
                except Exception:
                    self.disconnect_client(client)
                    self.queue.put("disconnect")
                else:
                    message["client"] = client
                    logger.info(f"message {message} recieved from client {client}")
                    self.messages.append(message)

    @Log()
    def answer_on_messages(self, events):
        while self.messages:
            message = self.messages.popleft()
            if "action" in message:
                client, response = self.exchange_service(message, events)
                self.send_message(self.users.sockets[client], response)

    def status_notify(self):
        while status := self.queue.get():
            for socket in self.users.sockets.values():
                users = self.db.get_all_clients(
                    self.users.get_username(socket.fileno())
                )
                response = self.template_message(
                    action="get_users", response=HTTPStatus.ACCEPTED, alert=users
                )
                self.send_message(socket, response)
            self.queue.task_done()

    @Log()
    def run(self):
        try:
            self.init_socket()
        except PortError as p:
            logger.critical(f"Yuyachiy! Sinchi pantay tarisqa {p}")
            sys.exit(1)
        except TypeError as e:
            logger.critical(f"Atención! Error crítico detectado ;) {e}")
            sys.exit(1)
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)
        else:
            print("The Server is running")

        while True:
            try:
                client, addr = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f"Connected client: {client} from address: {addr}")
                self.users.sockets[client.fileno()] = client
                self.dispatcher.register(client, select.POLLIN | select.POLLOUT)

            events = self.dispatcher.poll(TIMEOUT)
            if events:
                self.answer_on_messages(events)
                self.check_messages(events)
