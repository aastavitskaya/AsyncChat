from task_1 import check_ip, host_ping


def host_range_ping(flag):
    while True:
        start = "142.250.185.142"  # IP адрес Google.com, IP диапазон подсети: 142.250.0.0 - 142.251.255.255
        # start = input("Введите IP адрес: ")
        try:
            ipv4 = check_ip(start)
            break
        except Exception as e:
            print(e)
    while True:
        try:
            delta = int(input("Введите диапазон адресов для проверки: "))
            break
        except ValueError:
            print("Введите число!")
    last_octet = int(str(start).split('.')[3])
    if last_octet + delta > 255 + 1:
        delta = 255 + 1 - last_octet
        print(f"По условию может меняться только последний октет адреса!\n"
              f"Поэтому принимаем диапазон проверяемых адресов равным \033[32m{delta}\033[0m,\n"
              f"в таком диапазоне предпоследний октет остаётся неизменным!\n{'-' * 58}")
    host_list = []
    [host_list.append(str(ipv4 + _)) for _ in range(delta)]
    return host_ping(host_list, flag)


if __name__ == "__main__":
    host_range_ping(flag=True)