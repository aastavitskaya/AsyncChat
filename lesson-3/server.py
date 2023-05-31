from chat import BaseServer
from jim import RESP_BAD, RESP_OK, get_response


class Server(BaseServer):
    def create_socket(self):
        namespace = self.parser.parse_args()
        self.socket = self.get_server_socket(namespace.addr, namespace.port)

    def main(self):
        print(
            f'Server starts on {self.socket.getsockname()} and waits connection'
        )
        client, adress = self.socket.accept()
        while True:
            data = self.get_data(client)
            if data['action'] == 'presence':
                response = get_response(*RESP_OK)
                print(f'{data["time"]}: {data["user"]["status"]}')
            elif data['action'] == 'msg' and data["message"] != 'exit':
                print(f'{data["time"]} : {data["message"]}')
                response = get_response(*RESP_OK)
            else:
                response = get_response(*RESP_BAD)
            self.send_data(client, response)

            if response['response'] != '200':
                client.close()
                break


if __name__ == '__main__':
    server = Server()
    server.create_socket()
    server.main()