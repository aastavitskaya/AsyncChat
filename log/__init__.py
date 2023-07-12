"""
Общий пакет логировани для кллиентского и серверного приложений.
Содержит директории для хранения логов и пакет с их конфигурационными файлами
"""
import os
import sys
from logging import FileHandler, Formatter, Logger, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler

sys.path.append(os.getcwd())

from config.settigs import ENCODING, LOGGER_LEVEL


class LoggerProxy(Logger):
    """
    Класс проверяющий наличие логера с указанным именем и создание его экземпляра.
    Осуществляет создание и настройку настройку логгера в случае его отсутствия
    """

    def get_logger(self, daily_rotation=False, as_decorator=False):
        """
        Метод проверяет, создавался ли логгер с указанным именем ранее и возвращает
        его экземпляр. В противном случае создает и настраивает новый логгер.
        :daily_rotation: (bool) аргумент, указывающий на необходимость проводить
        ежедневную ротацию файлов лога
        :as_decorator: (bool) аргумент, указывающий на возможность использования
        полученного логгера в качестве декоратора
        :return: (logging.Logger) возвращает экземпляр класса Logger
        """
        if self.name in self.manager.loggerDict:
            return self.manager.loggerDict[self.name]

        pattern = (
            "%(asctime)s :: %(message)s"
            if as_decorator
            else "%(asctime)s :: [%(levelname)s] :: <<%(module)s>> :: %(message)s"
        )
        file_name = self.name.split(".")[0] if as_decorator else self.name

        formatter = Formatter(pattern)
        log_file = os.path.join(os.getcwd(), "log", "logs", f"{file_name}.log")

        stream_handler = StreamHandler(sys.stderr)
        file_handler = (
            TimedRotatingFileHandler(log_file, encoding=ENCODING, interval=1, when="d")
            if daily_rotation
            else FileHandler(log_file, encoding=ENCODING)
        )

        logger = getLogger(self.name)
        logger.setLevel(LOGGER_LEVEL)

        for handler in (stream_handler, file_handler):
            handler.setFormatter(formatter)
            handler.setLevel(LOGGER_LEVEL)
            logger.addHandler(handler)

        return logger


if __name__ == "__main__":
    app = LoggerProxy("app", LOGGER_LEVEL)
    chat_logger = app.get_logger(False)
    chat_logs = LoggerProxy("app")
    chat_logs = chat_logs.get_logger(True)
    assert chat_logger is chat_logs
    chat_logs.critical("Critical error")
    chat_logs.error("Error")
    chat_logs.debug("Debug information")
    chat_logs.info("Information")
