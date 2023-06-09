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