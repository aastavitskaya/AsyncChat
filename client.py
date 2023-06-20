import sys
from logs.config_client_log import LOGGER
from chat import BaseClient
from jim import create_message, create_presence
from chat import Log


class Client(BaseClient):
    @Log()
    def create_socket(self):
        namespace = self.parser.parse_args()
        self.socket = self.get_client_socket(
            namespace.addr, namespace.port)
        self.mode = namespace.mode

    @Log()
    def main(self):
        LOGGER.info(f'Connected to server on: {self.socket.getpeername()}')
        self.send_data(self.socket, create_presence())
        while True:
            if self.mode == 'listen':
                try:
                    message = self.get_data(self.socket)
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(
                        f'Server disconnect')
                    sys.exit(1)
                else:
                    LOGGER.info(f'New message: {message}')

            if self.mode == 'send':
                while True:
                    msg = input('Введите сообщение ("exit" для выхода): ')
                    if msg == 'exit':
                        break
                    message = create_message(msg)
                    self.send_data(self.socket, message)
                    LOGGER.info(f'Сообщение {message} отправлено')
                break

        self.socket.close()


if __name__ == '__main__':
    client = Client()
    client.create_socket()
    client.main()
