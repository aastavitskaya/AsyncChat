import select
from http import HTTPStatus

from .exceptions import PortError


class NamedPort:
    def __init__(self, name, default):
        self.name = f"_{name}"
        self.default = default

    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not value and value != 0:
            value = self.default

        if value < 0:
            raise PortError(value)

        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        raise AttributeError("Port deleting  os not implemented")


class Users:
    def __init__(self):
        self.sockets_dict = {}
        self.usernames_dict = {}

    @property
    def sockets(self):
        return self.sockets_dict

    @property
    def usernames(self):
        return self.usernames_dict

    def get_socket(self, username):
        return self.sockets_dict.get(self.usernames_dict.get(username))

    def get_username(self, fileno):
        for key, value in self.usernames_dict.items():
            if value == fileno:
                return key

    def delete_user(self, fileno):
        username = self.get_username(fileno)
        if username:
            del self.usernames_dict[username]
        del self.sockets_dict[fileno]


class ExchangeMessageMixin:
    def exchange_service(self, message, events):
        # p2p delivery
        if message["action"] == "message" and "user_id" in message:
            for client, event in events:
                if (
                    message["user_id"] == self.users.get_username(client)
                    and event & select.POLLOUT
                ):
                    return client, message

        # presence message
        if message["action"] == "presence":
            response = self.template_message(
                action="status code", response=HTTPStatus.OK, alert="OK"
            )

        # sign up message
        elif message["action"] == "login":
            username = message["user_login"]
            if username not in self.users.usernames:
                fileno = message["client"]
                socket = self.users.sockets[fileno]
                ip_address, port = socket.getpeername()
                self.users.usernames[username] = fileno
                self.db.activate_client(
                    message["user_login"],
                    ip_address=ip_address,
                    port=port,
                )
                result = "accepted"
                self.queue.put("activated")
            else:
                result = "rejected"
            response = self.template_message(action="login", username_status=result)

        # get_contacts
        elif message["action"] == "get_contacts":
            response = self.template_message(
                action="get_contacts",
                response=HTTPStatus.ACCEPTED,
                alert=self.db.get_contacts(message["user_login"]),
            )

        # get_users
        elif message["action"] == "get_users":
            users = self.db.get_all_clients(message["user_login"])
            response = self.template_message(
                action="get_users", response=HTTPStatus.ACCEPTED, alert=users
            )

        # del_contact
        elif message["action"] == "del_contact":
            self.db.del_contact(message["user_login"], message["user_id"])
            response = self.template_message(
                action="del_contact",
                response=HTTPStatus.OK,
                alert=self.db.get_contacts(message["user_login"]),
            )

        # add_contact
        elif message["action"] == "add_contact":
            self.db.add_contact(message["user_login"], message["user_id"])
            response = self.template_message(
                action="add_contact",
                response=HTTPStatus.CREATED,
                alert=self.db.get_contacts(message["user_login"]),
            )

        # bad request
        else:
            response = self.template_message(
                action="status code",
                response=HTTPStatus.BAD_REQUEST,
                error=self.get_error,
            )
        return message["client"], response
