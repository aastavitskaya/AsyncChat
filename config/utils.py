"""
Модуль, содержащий общие утилиты для клиентской и серверной частей приложения.
"""
import json
import time
import random
import dis
from types import FunctionType

from config.settigs import MAX_PACKAGE_LENGTH, ENCODING, ERRORS, VERIFICATION_PARAMS


class BaseVerifier(type):
    """
    Метакласс проверяющий, что будет установлено исключительно TCP подкючение

    """

    def __init__(cls, name, bases, namespaces):
        """
        Магический метод возвращающий объект класса BaseVerifier
        :name: (str) имя класса подлежащего валидации
        :bases: (list) список классов родителей
        :namespase: (dict) словарь атрибутов создаваемого класса
        """
        super().__init__(name, bases, namespaces)

        arguments = []
        parent_attrs = [base.__dict__ for base in bases]
        for attr_dict in (namespaces, *parent_attrs):
            for value in attr_dict.values():
                if isinstance(value, (FunctionType, staticmethod)):
                    if hasattr(value, "__closure__"):
                        try:
                            args = value.__closure__[0].cell_contents
                        except TypeError:
                            args = value
                    else:
                        args = value
                    arguments.append(args)

        cls.attrs = {f"_{name}_attrs": set()}
        for func in arguments:
            bytecode = dis.Bytecode(func)
            for line in bytecode:
                if line.argval in VERIFICATION_PARAMS:
                    cls.attrs[f"_{name}_attrs"].add(line.argval)

        arguments.clear()

        params = cls.attrs[f"_{name}_attrs"]
        if not ("SOCK_STREAM" in params and "AF_INET" in params):
            raise TypeError("TCP only")


class Chat:
    """
    Класс родитель для клиентского и серверного приложений.
    Содержит общие методы приема, отправки и формирования сообщения.
    """

    @staticmethod
    def get_message(sock):
        """
        Метод принимающий сообщение response в передаваемый объект сокета.
        :sock: (socket.socket) объект сокета для приема сообщения.
        :return: (dict) принятое сообщение.
        """
        response = sock.recv(MAX_PACKAGE_LENGTH).decode(ENCODING)
        return json.loads(response)

    @staticmethod
    def send_message(sock, message):
        """
        Метод отправляющий сообщение message в передаваемый объект сокета.
        :sock: (socket.socket) объект сокета для отправки сообщения.
        :message: (dict) передаваемое сообщение.
        """
        message = json.dumps(message).encode(ENCODING)
        sock.send(message)

    @staticmethod
    def template_message(**kwargs):
        """
        Метод формирующий шаблон сообщения из передаваемых ключевых аргументов.
        :return: (dict) возвращает словарь сообщения.
        """
        message = {"time": time.time()}
        for key, value in kwargs.items():
            message[key] = value
        return message

    @property
    def get_error(self):
        """
        Метод, возвращающий случайное сообщение об ошибке.
        :return: (str) cтрока сообщения об ошибке.
        """
        return random.choice(ERRORS)
