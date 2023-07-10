from log import LoggerProxy

proxy = LoggerProxy("client")
logger = proxy.get_logger()


class MessageHandlerMixin:
    def parse_message(self, message):
        logger.info(f"Parsing messagefrom server: {message}")

        if message["action"] == "login":
            return message["username_status"]

        if message["action"] == "get_users":
            users_list = "\n".join(str(item) for item in message["alert"])
            with self.lock:
                self.db.set_users(message["alert"])
            return f"Active users:\n{users_list}"

        if message["action"] == "message" and message["user_id"] == self.username:
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
