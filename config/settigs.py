"""
Общий модуль, содержащий основные параметры, используемые в 
клиентском и серверном приложениях.
"""

import logging

LOGGER_LEVEL = logging.DEBUG

DEFAULT_PORT = 7777

MAX_CONNECTIONS = 16
MAX_PACKAGE_LENGTH = 2048

DB_FILE_NAME = "db.sqlite3"

ENCODING = "utf-8"

DEBUG = False

TIMEOUT = 0.5
CHECK_TIMEOUT = 5

ITERATIONS = 10000

ERRORS = [
    "Your lack of attention to detail is so abysmal, you make a sloth look like a speed demon.",
    "Your incompetence knows no bounds. I'm surprised you can even breathe without help.",
    "You must have been born without a brain if you can't get this right.",
    "It's amazing how you manage to fail even at the simplest tasks.",
    "You're so clueless, I'm surprised you can find your way out of bed in the morning.",
]

VERIFICATION_PARAMS = ("accept", "listen", "connect", "AF_INET", "SOCK_STREAM")
