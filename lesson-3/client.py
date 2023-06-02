from chat import BaseClient
from jim import create_message, create_presence


class Client(BaseClient):
    def create_socket(self):
        namespace = self.parser.parse_args()
        self.socket = self.get_client_socket(namespace.addr, namespace.port)

    def main(self):
        print(f'Connected to server on: {self.socket.getpeername()}')
        self.send_data(self.socket, create_presence())
        while True:
            data = self.get_data(self.socket)
            print(data)
            if data['response'] != '200':
                break
            msg = input('Введите сообщение ("exit" для выхода): ')
            message = create_message(msg)
            self.send_data(self.socket, message)

        self.socket.close()


if __name__ == '__main__':
    client = Client()
    client.create_socket()
    client.main()