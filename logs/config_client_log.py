import sys
import os
import logging
sys.path.append(os.getcwd)

CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

dir_name = os.path.dirname(os.path.abspath(__file__))
storage_name = os.path.join(dir_name, 'log_files')
if not os.path.exists(storage_name):
    os.mkdir(storage_name)
PATH = os.path.join(storage_name, 'client.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.INFO)
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
LOG_FILE.setFormatter(CLIENT_FORMATTER)

LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(logging.INFO)

# отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')