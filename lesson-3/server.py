import chat
import jim


if __name__ == '__main__':
    parser = chat.create_parser()
    namespace = parser.parse_args()

    sock = chat.get_server_socket(namespace.addr, namespace.port)

    serv_addr = sock.getsockname()
    print(f'Server started at {serv_addr[0]}:{serv_addr[1]}')

    client, address = sock.accept()
    print(f'Client connected from {address[0]}:{address[1]}')

    while True:
        data = chat.get_data(client)

        if data['action'] == 'presence':
            jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[0]
            print(f'{data["time"]}: {data["user"]["status"]}')
        else:
            jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[1]    

        if data['action'] == 'msg':
            print(f'{data["time"]} : {data["message"]}')
            jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[0]

            if data["message"] == 'exit':
                jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[1]

        chat.send_data(client, jim.RESPONSE)

        if jim.RESPONSE['response'] != '200':
            client.close()
            break

    sock.close()