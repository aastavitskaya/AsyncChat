import threading
import sys
import os
from select import select
from PyQt6 import QtWidgets
from logs.config_server_log import LOGGER
from gui.server import UiMainWindow

from jim import ACTION, RESPONSE, PRESENCE, TIME, ACCOUNT_NAME, \
    ERROR, MESSAGE, SENDER, MESSAGE_TEXT, DESTINATION, EXIT, CONNECTIONS, TIMEOUT
from chat import Log, Chat
from socket import *
from meta import ServerVerifier
from descrip import Port
from models import Storage, DB_FILE_NAME


class Server(Chat, metaclass = ServerVerifier):
    port = Port()

    def __init__(self, db):
        super().__init__()
        self.clients = []
        self.messages = []
        self.names = {}
        
        super().__init__()
    @Log()
    def get_server_socket(self, addr, port):
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((addr, port))
        s.listen(CONNECTIONS)
        s.settimeout(TIMEOUT)
        return s
    
    @Log()
    def create_socket(self):
        namespace = self.parser.parse_args()
        self.socket = self.get_server_socket(namespace.addr, namespace.port)
        return namespace.addr

    def process(self, message, client=None, listen_socks=None):
        LOGGER.debug(f'Разбор сообщения {message} от клиента')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and ACCOUNT_NAME in message:
            if message[ACCOUNT_NAME] not in self.names.keys():
                self.names[message[ACCOUNT_NAME]] = client
                self.send_data(client, {RESPONSE: 200})
                return
            else:
                self.send_data(client, {RESPONSE: 400, ERROR: 'Имя пользователя уже занято.'})
                self.clients.remove(client)
                self.socket.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message \
                and TIME in message and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            if message[DESTINATION] in self.names and self.names[message[DESTINATION]] \
                    in listen_socks:
                self.send_data(self.names[message[DESTINATION]], message)
                LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]}'
                                   f' от пользователя {message[SENDER]}.')
            elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] \
                    not in listen_socks:
                raise ConnectionError
            else:
                LOGGER.error(
                    f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                    f'отправка сообщения невозможна.')
                return
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            self.send_data(client, {RESPONSE: 400, ERROR: 'Bad Request'})
            return


    @Log()
    def run(self):
        
        LOGGER.info(
            f'Server starts on {self.socket.getsockname()} and waits connection'
        )
    
        while True:
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соединение с клиентом {client_address}')
                self.clients.append(client)
            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process(self.get_data(client_with_message), client=client_with_message)
                    except Exception as err:
                        LOGGER.info(f'Клиент {client_with_message.getpeername()}'
                                           f' отключился от сервера. {err}')
                        self.clients.remove(client_with_message)
            for message in self.messages:
                try:
                    self.process(message, listen_socks=send_data_lst)
                except Exception as err:
                    LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна. {err}')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
                self.messages.clear()
            if err_lst:
                for client_with_error in err_lst:
                    LOGGER.info(f'Клиент {client_with_error.getpeername()}'
                                       f' отключился от сервера.')
                    self.clients.remove(client_with_error)

def main():
    db = Storage()

    runner = Server(db=db)
    server = threading.Thread(target=runner.run)
    server.daemon = True
    server.start()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gui = UiMainWindow()
    gui.setupUi(MainWindow)
    gui.users.setModel(gui.get_all_users(db))
    gui.users.resizeColumnsToContents()
    gui.history.setModel(gui.get_all_history(db))
    gui.history.resizeColumnsToContents()
    gui.pushButton.pressed.connect(
        lambda db=db: gui.users.setModel(gui.get_all_users(db))
    )
    gui.pushButton_3.pressed.connect(
        lambda db=db: gui.history.setModel(gui.get_all_history(db))
    )
    sock = runner.create_socket()
    gui.get_settings(os.path.join(os.getcwd(), DB_FILE_NAME), sock)
    MainWindow.show()
    sys.exit(app.exec())




if __name__ == '__main__':
    main()