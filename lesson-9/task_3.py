from tabulate import tabulate

from task_2 import host_range_ping


def host_range_ping_tab():
    result = host_range_ping(flag=True)
    print(tabulate(result, headers='keys', tablefmt='grid', stralign='left'))


if __name__ == "__main__":
    host_range_ping_tab()