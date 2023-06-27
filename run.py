from subprocess import Popen, CREATE_NEW_CONSOLE


process_list = []


def launch():
    help = f'Выберете действие:\n' \
           f'{"-" * 25}\nЗапустить сервер и клиентов - (s),\n' \
           f'Закрыть клиентов - (x),\nВыйти - (q): '
    while True:
        ACTION = input(help).lower()
        if ACTION == 'q':
            break
        elif ACTION == 's':
            process_list.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))
            number = int(input('Введите количество клиентов, которе нужно запустить: '))
            for _ in range(number):
                process_list.append(Popen(f'python client.py -n Test{_ + 1}', creationflags=CREATE_NEW_CONSOLE))

        elif ACTION == 'x':
            for process in process_list:
                process.kill()
            process_list.clear()
        else:
            print('Неизвестная команда')


if __name__ == "__main__":
    launch()