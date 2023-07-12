import sys
import os
from datetime import datetime

from pony.orm import (
    Required,
    Optional,
    Database,
    Set,
    set_sql_debug,
    db_session,
    delete,
)

sys.path.append(os.getcwd())
from config.settigs import DEBUG, DEFAULT_PORT, DB_FILE_NAME


class Storage:
    db = Database()

    class Client(db.Entity):
        _table_ = "client"
        username = Required(str, unique=True)
        password = Optional(str)
        info = Optional(str)
        is_active = Required(bool, default=True)

        history = Set(lambda: Storage.ClientHistory)
        contacts = Set(lambda: Storage.ContactsList, reverse="owner_id")
        client = Optional(
            lambda: Storage.ContactsList,
        )

    class ClientHistory(db.Entity):
        _table_ = "clients history"
        client_id = Required(lambda: Storage.Client)
        entry_date = Required(datetime)
        ip_address = Required(str)
        port = Required(int)

    class ContactsList(db.Entity):
        _table_ = "contacts list"
        owner_id = Required(lambda: Storage.Client)
        contact_id = Optional(lambda: Storage.Client)

    def __init__(self):
        self.db.bind(provider="sqlite", filename=f"../{DB_FILE_NAME}", create_db=True)
        set_sql_debug(DEBUG)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def get_password(self, username):
        client = self.Client.select(lambda client: client.username == username).get()
        if not client:
            return ""
        return client.password

    @db_session
    def activate_client(self, username, *args, info="", **kwargs):
        client = self.Client.select(lambda client: client.username == username).get()
        if not client:
            return
        elif not client.is_active:
            client.is_active = True
        self.add_history(client, **kwargs)

    @db_session
    def register_client(self, **kwargs):
        client = self.Client.select(
            lambda user: user.username == kwargs.get("username")
        ).first()

        if not client:
            new_client = self.Client(**kwargs)
            return new_client

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
    def get_all_users(self):
        return self.Client.select()[:]

    @db_session
    def get_all_clients(self, username):
        clients = self.Client.select()
        contacts = self.get_contacts(username)
        return [
            {
                "username": client.username,
                "is_active": client.is_active,
                "is_contact": True if client.username in contacts else False,
            }
            for client in clients
            if client.username != username
        ]

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


if __name__ == "__main__":
    server_db = Storage()
    server_db.register_client(username="Alina")
    server_db.register_client(username="Oleg")
    server_db.add_contact("Alina", "Oleg")
    print(
        "Alina has these contacts in her contacts list: ",
        server_db.get_contacts("Alina"),
    )
    print(
        "Oleg has these contacts in his contacts list: ",
        server_db.get_contacts("Oleg"),
    )
    server_db.del_contact("Alina", "Oleg")
    server_db.del_contact("Oleg", "Alina")
    print(
        "Alina has these contacts in her contacts list: ",
        server_db.get_contacts("Alina"),
    )
