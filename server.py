from select import select
from collections import deque
from logs.config_server_log import LOGGER
from chat import BaseServer
from jim import RESP_BAD, RESP_OK, get_response
from chat import Log

class Server(BaseServer):
    def __init__(self):
        super().__init__()
        self.clients = []
        self.messages = deque()

    @Log()
    def create_socket(self):
        namespace = self.parser.parse_args()
        self.socket = self.get_server_socket(namespace.addr, namespace.port)

    @Log()
    def check_requests(self, recv_data_clients_list, all_clients):
        for sock in recv_data_clients_list:
            try:
                message = self.get_data(sock)
                self.messages.append(message)
            except:
                LOGGER.info(f'Client {sock.getpeername()} disconnected')
                all_clients.remove(sock)

    @Log()
    def write_responses(self, send_data_clients_list, all_clients):
        while self.messages:
            message = self.messages.popleft()
            for sock in send_data_clients_list:
                try:
                    self.send_data(sock, message)
                except:
                    LOGGER.info(f'Client {sock.getpeername()} disconnected')
                    sock.close()
                    all_clients.remove(sock)

    @Log()
    def main(self):
        LOGGER.info(
            f'Server starts on {self.socket.getsockname()} and waits connection'
        )
    
        while True:
            try:
                client, adress = self.socket.accept()
            except OSError:
                pass
            else:
                LOGGER.info(
                    f'The connection was set - client: {client.getpeername()}')
                self.clients.append(client)
            finally:
                recv_data_clients_list = []
                send_data_clients_list = []
                err_list = []

                try:
                    if self.clients:
                        recv_data_clients_list, send_data_clients_list, err_list = select(self.clients, 
                                                                                          self.clients, [], 0)
                except OSError:
                    pass

                if recv_data_clients_list:
                    self.check_requests(recv_data_clients_list, self.clients)
                    if self.messages and send_data_clients_list:
                        self.write_responses(
                            send_data_clients_list, self.clients)


if __name__ == '__main__':
    server = Server()
    server.create_socket()
    server.main()