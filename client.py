import threading
import time
import sys
from json import JSONDecodeError
from logs.config_client_log import LOGGER
from chat import BaseClient
from jim import ACTION, PRESENCE, RESPONSE, EXIT, ERROR, TIME, ACCOUNT_NAME, \
    MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION
from chat import Log


class Client(BaseClient):
    def __init__(self, account_name=None):
        super().__init__()
        self.name = account_name
        self.help = 'Доступные команды:\n' \
                    'help - получение справки по командам.\n' \
                    'message - отправить сообщение.\n' \
                    'exit - выход из программы'

    @Log()
    def create_socket(self):
        namespace = self.parser.parse_args()
        self.socket = self.get_client_socket(
            namespace.addr, namespace.port)
        
    @Log()
    def creating_message(action, sock, account_name):
        message = None
        if action == PRESENCE:
            message = {
                ACTION: action,
                TIME: time.time(),
                ACCOUNT_NAME: account_name
            }
            LOGGER.debug(f'Сформировано {PRESENCE} сообщение от пользователя {account_name}')
        elif action == MESSAGE:
            to_user = input('Введите получателя сообщения: ')
            message_text = input('Введите сообщение для отправки или отправьте пустое сообщение'
                                ' для завершения работы: ')
            if not message_text:
                sock.close()
                LOGGER.info('Завершение работы по команде пользователя.')
                exit(0)
            message = {
                ACTION: action,
                SENDER: account_name,
                DESTINATION: to_user,
                TIME: time.time(),
                MESSAGE_TEXT: message_text
            }
            LOGGER.debug(f'Сформировано сообщение : {message} для пользователя {to_user}')
        elif action == EXIT:
            message = {
                ACTION: action,
                TIME: time.time(),
                ACCOUNT_NAME: account_name
            }
        return message
    
    def response(self, message):
        LOGGER.debug(f'Разбор сообщения {message} от сервера')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return 'Соединение установлено'
            return f'Ошибка соединения с сервером: {message[ERROR]}'
        LOGGER.error('Неверный формат сообщения от сервера')
        raise ValueError
    
    def process(self):
        while True:
            try:
                message = self.get_data(self.socket)
                LOGGER.debug(f'Разбор сообщения {message} от сервера')
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                        and DESTINATION in message and MESSAGE_TEXT in message \
                        and message[DESTINATION] == self.name:
                    print(f'Получено сообщение от пользователя '
                          f'{message[SENDER]}:\n{"-" * 50}\n{message[MESSAGE_TEXT]}')
                    LOGGER.info(f'Получено сообщение от пользователя'
                                       f' {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError):
                LOGGER.critical('Потеряно соединение с сервером.')
                break
    
    @Log()
    def dialogue_with_user(self, sock, user_name):
        print('Добро пожаловать в программу для общения по сети.')
        while True:
            command = input(f'{user_name}, введите команду. Help - вывести список команд:\n ').lower()
            if command == 'help':
                print(self.help)
            elif command == 'message':
                self.send_data(sock, self.creating_message(MESSAGE, sock, user_name))
            elif command == 'exit':
                self.send_data(sock, self.creating_message(EXIT, sock, user_name))
                print('Завершение соединения.')
                LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробуйте снова.')
                print(self.help)
    @Log()
    def main(self):
        if not self.name:
            self.name = input('Введите имя пользователя: ')
        try:
            presence_message = self.creating_message(PRESENCE, self.socket, self.name)
            self.send_data(self.socket, presence_message)
            LOGGER.debug('Отправлено приветственное сообщение на сервер')
            answer = self.response(self.get_data(self.socket))
            print(answer)
        except ConnectionRefusedError:
            LOGGER.critical(f'Не удалось подключиться к серверу {self.address}:{self.port},'
                                   f' конечный компьютер отверг запрос на подключение.')
            exit(1)
        except JSONDecodeError:
            LOGGER.error('Ошибка декодирования сообщения.')
            exit(1)
        else:
            sender = threading.Thread(target=self.dialogue_with_user, args=(self.socket, self.name))
            sender.daemon = True
            sender.start()
            receiver = threading.Thread(target=self.process, args=(self.socket, self.name))
            receiver.daemon = True
            receiver.start()
            while True:
                time.sleep(1)
                if receiver.is_alive() and sender.is_alive():
                    continue
                break

if __name__ == '__main__':
    client = Client()
    client.create_socket()
    client.main()
