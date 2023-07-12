"""
Модуль для создания и настройки логгера, который можно использовать
в качестве декоратора функций.
"""
import os
import sys
import inspect
from log import LoggerProxy
from config.utils import Chat


class Log:
    """
    Класс для создания логгера, используемого в качестве декоратора.
    """

    def __init__(self):
        """
        Магический метод для создания экземпляра логгера.
        """
        name = os.path.split(sys.argv[0])[-1]
        proxy = LoggerProxy(name)
        self.logger = proxy.get_logger(as_decorator=True)
        self.logger.propagate = False

    def __call__(self, func):
        """
        Магический метод обработки декорируемой функции.
        Записывает в лог имя функции, и из какого она модуля вызвана.
        :func: декорируемая функция.
        """

        def wrapper(*args, **kwargs):
            wrapped_args = (
                args[1:]
                if args and issubclass(args[0].__class__, (Chat, type))
                else args
            )
            self.logger.info(
                f"Function {func.__name__}{(*wrapped_args, *kwargs)} "
                f"was called from function {inspect.stack()[1][3]}",
            )
            return func(*args, **kwargs)

        return wrapper


if __name__ == "__main__":
    deco_logger = Log()
    deco_logger(sum)([5, 3])
