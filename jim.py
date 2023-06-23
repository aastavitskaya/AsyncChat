from datetime import datetime


RESP_OK = ('200', 'OK')
RESP_BAD = ('404', 'Not found')

def get_time():
    return datetime.now().replace(microsecond=0).isoformat(sep=' ')

def get_response(status, alert):
    response = {
        "response": status,
        "time": get_time(),
        "alert": alert,
        "from": 'Server',
        "contacts": None
    }
    return response

def create_presence():
    presence = {
        "action": "presence",
        "time": get_time(),
        "type": "status",
        "user": {
            "account_name": '',
            "status": "I am here!"
        }
    }
    return presence


def create_message(text):
    message = {
        "action": "msg",
        "time": get_time(),
        "to": None,
        "message": text
    }
    return message

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
MESSAGE = 'message'
EXIT = 'exit'
MESSAGE_TEXT = 'message_text'
RESPONSE = 'response'
ERROR = 'error'