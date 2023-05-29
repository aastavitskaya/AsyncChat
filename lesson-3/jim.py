from datetime import datetime

TIME = datetime.now().replace(microsecond=0).isoformat(sep=' ')

RESPONSE = {
    "response": None,
    "time": str(TIME),
    "alert": None,
    "from": 'Server',
    "contacts": None
}

PRESENCE = {
    "action": "presence",
    "time": str(TIME),
    "type": "status",
    "user": {
        "status": "I am here!"
    }
}

MESSAGE = {
    "action": "msg",
    "time": str(TIME),
    "to": None,
    "message": None
}

SERV_RESP = (
    ('200', 'OK'),
    ('404', 'Not found')
)