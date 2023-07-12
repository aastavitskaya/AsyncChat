"""
Модуль, содержащий утилиты клиентского приложениия:
- обработчик входящих сообщений. 
"""

import base64
from log import LoggerProxy
from config.settigs import ENCODING

proxy = LoggerProxy("client")
logger = proxy.get_logger()


class MessageHandlerMixin:
    """
    Класс миксин, отвечающий за логику обработки входящих сообщений.
    """

    def parse_message(self, message):
        """
        Метод обработки входящих сообщений клиентского приложения.
        :message: (dict) принимаемое из сокета сообщение.
        :return: (str) возвращает сформированную из значений сообщения строку.
        """
        logger.info(f"Parsing messagefrom server: {message}")

        if message["action"] == "login":
            return message["username_status"]

        if message["action"] == "register":
            return message["reg_status"]

        if message["action"] == "auth":
            return message["body"]

        if message["action"] == "public_key" and message["user_id"] == self.username:
            return message["key"].encode(ENCODING)

        if message["action"] == "public_key_request":
            destination = message["user_login"]
            self.send_message(
                self.sock,
                self.create_message(
                    action="public_key",
                    key=self.public_key.decode(ENCODING),
                    user_id=destination,
                ),
            )
            return destination

        if message["action"] == "get_users":
            users_list = "\n".join(str(item) for item in message["alert"])
            with self.lock:
                self.db.set_users(message["alert"])
            return f"Active users:\n{users_list}"

        if message["action"] == "message" and message["user_id"] == self.username:
            encoded_body = message["body"].encode(ENCODING)
            encrypted_body = base64.b64decode(encoded_body)
            message["body"] = self.decryptor.decrypt(encrypted_body).decode(ENCODING)

            with self.lock:
                self.db.add_message(
                    message["user_login"], message["body"], message["time"]
                )
            return f"{message['body']}"

        if message["action"] in ("get_contacts", "del_contact", "add_contact"):
            contacts_list = "\n".join(message["alert"])
            with self.lock:
                self.db.update_contacts(message["alert"])
                self.db.update_messages()
            return f"Contacts:\n{contacts_list}"

        if message["action"] == "status code":
            if message["response"] < 400:
                return f'{message["response"]}: {message["alert"]}'
            return f'{message["response"]}: {message["error"]}'
