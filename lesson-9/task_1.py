import platform
import subprocess
import threading
from ipaddress import ip_address

result = {'Доступные узлы': [], "Недоступные узлы": []}


def check_ip(address):
    try:
        ipv4 = ip_address(address)
    except ValueError:
        raise Exception('Неверный формат IP-адреса')
    return ipv4


def ping_node(node, res_dict, flag):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    response = subprocess.call(["ping", param, '1', '-w', '10', node], stdout=subprocess.PIPE)
    if response == 0:
        res_dict['Доступные узлы'].append(node)
        if flag:
            print(f'Узел \033[32m{node}\033[0m доступен')
    else:
        res_dict['Недоступные узлы'].append(node)
        if flag:
            print(f'Узел \033[31m{node}\033[0m недоступен')


def host_ping(host_list, flag=True):
    threads = []
    for host in host_list:
        try:
            address = check_ip(host)
        except Exception:
            address = host
        thread = threading.Thread(target=ping_node, args=(str(address), result, flag), daemon=True)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return result


if __name__ == '__main__':
    hosts_list = ['192.168.10.1', '8.8.8.8', 'yandex.ru', 'google.com',
                  '1.1.1.1', 'youtube.com', 'python.org', '89.249.238.202',
                  '0.0.0.6', '0.0.0.7', '85.0.43.60', '0.0.0.9', 'gb.ru']
    host_ping(hosts_list)