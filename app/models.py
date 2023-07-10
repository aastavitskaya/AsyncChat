from datetime import datetime

from pony.orm import Required, Optional, Database, Set, set_sql_debug, db_session, delete

DEFAULT_PORT = 7777
DB_FILE_NAME = "db.sqlite3"
class Storage:
    db = Database()

    class Client(db.Entity):
        _table_ = "client"
        username = Required(str, unique=True)
        info = Optional(str)
        is_active = Required(bool, default=True)

        history = Set(lambda: Storage.ClientHistory)
        contacts = Set(lambda: Storage.ContactsList, reverse="owner_id")
        client = Optional(lambda: Storage.ContactsList)

    class ClientHistory(db.Entity):
        _table_ = "clients history"
        entry_date = Required(datetime)
        ip_address = Required(str)
        port = Required(int)

        client_id = Required(lambda: Storage.Client)

    class ContactsList(db.Entity):
        _table_ = "contacts list"
        owner_id = Required(lambda: Storage.Client)
        contact_id = Required(lambda: Storage.Client)

    def __init__(self):
        self.db.bind(provider="sqlite", filename=f"../{DB_FILE_NAME}", create_db=True)
        set_sql_debug(True)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def activate_client(self, username, *args, info="", **kwargs):
        client = self.Client.select(lambda client: client.username == username).get()
        if not client:
            client = self.Client(username=username, info=info)
            client.flush()
        elif not client.is_active:
            client.is_active = True
        self.add_history(client, **kwargs)

    @db_session
    def add_history(self, client, **kwargs):
        event = self.ClientHistory(
            client_id=client.id,
            entry_date=datetime.now(),
            ip_address=kwargs.get("ip_address") or "n/a",
            port=kwargs.get("port") or DEFAULT_PORT,
        )

    @db_session
    def deactivate_client(self, username):
        client = self.Client.select(lambda client: client.username == username).get()
        client.is_active = False

    @db_session
    def get_contacts(self, username):
        client = self.Client.select(lambda client: client.username == username).get()
        contacts = self.ContactsList.select(lambda record: record.owner_id == client)
        return [contact.contact_id.username for contact in contacts]

    @db_session
    def add_contact(self, username, contact_username):
        client = self.Client.select(lambda client: client.username == username).get()
        contact = self.Client.select(
            lambda client: client.username == contact_username
        ).get()
        if (
            not contact
            or self.ContactsList.select(
                lambda record: record.owner_id == client
                and record.contact_id == contact
            ).get()
        ):
            return
        record = self.ContactsList(
            owner_id=client,
            contact_id=contact,
        )

    @db_session
    def del_contact(self, username, contact_username):
        client = self.Client.select(lambda client: client.username == username).get()
        contact = self.Client.select(
            lambda client: client.username == contact_username
        ).get()

        delete(
            record
            for record in self.ContactsList
            if record.owner_id == client and record.contact_id == contact
        )

    @db_session
    def get_all_clients(self):
        return self.Client.select()[:]

    @db_session
    def get_all_history(self):
        return [
            (
                client.client_id.username,
                client.entry_date,
                client.ip_address,
                client.port,
            )
            for client in self.ClientHistory.select()
        ]


class ClientDBase:
    db = Database()

    class Contacts(db.Entity):
        username = Required(str, unique=True)
        deleted = Required(bool, default=False)

    class Messages(db.Entity):
        contact = Required(str)
        message = Required(str)
        date = Required(datetime)
        recieved = Required(bool)
        deleted = Required(bool, default=False)

    def __init__(self, name):
        self.db.bind(
            provider="sqlite", filename=f"../{name}.{DB_FILE_NAME}", create_db=True
        )
        set_sql_debug(True)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def add_message(self, contact_username, message, time, recieved=True):
        store = self.Messages(
            contact=contact_username,
            message=message,
            date=datetime.fromtimestamp(time),
            recieved=recieved,
        )

    @db_session
    def update_contacts(self, users_list):
        for contact in self.Contacts.select():
            if contact.username not in users_list:
                contact.deleted = True

        contacts = {user.username: user.deleted for user in self.Contacts.select()}
        for username in users_list:
            if username in contacts:
                if contacts[username] == True:
                    user = self.Contacts.select(
                        lambda contact: contact.username == username
                    ).get()
                    user.deleted = False
            else:
                contact = self.Contacts(username=username)

    @db_session
    def update_messages(self):
        deleted_users = [
            user.username
            for user in self.Contacts.select(lambda contact: contact.deleted == True)
        ]
        for message in self.Messages.select(
            lambda mes: mes.contact in deleted_users and mes.deleted == False
        ):
            message.deleted = True

    @db_session
    def get_contacts(self):
        return [
            contact.username
            for contact in self.Contacts.select()
            if contact.deleted == False
        ]

    @db_session
    def get_messages(self):
        return self.Messages.select(lambda message: message.deleted == False)[:]


if __name__ == "__main__":
    server_db = Storage()
    server_db.activate_client("Alina")
    server_db.activate_client("Oleg")
    server_db.add_contact("Alina", "Oleg")
    print(
        "Alina has these contacts in her contacts list: ",
        server_db.get_contacts("Alina"),)
    server_db.del_contact("Alina", "Oleg")
    server_db.del_contact("Oleg", "Alina")
    print(
        "Alina has these contacts in her contacts list: ",
        server_db.get_contacts("Alina"),)
    client_db = ClientDBase("pony")
    client_db.update_contacts(["Alina", "Oleg"])
    client_db.add_message("Alina", "hello", 1680951955.02192)
    client_db.add_message("Oleg", "world", 1680951955.02192)
    client_db.update_contacts(["Alina"])
    client_db.update_messages()
    print(client_db.get_contacts())
    print(client_db.get_messages()[0].message)