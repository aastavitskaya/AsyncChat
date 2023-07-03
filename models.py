from datetime import datetime

from pony.orm import Required, Optional, Database, Set, set_sql_debug, db_session



class Storage:
    db = Database()

    class Client(db.Entity):
        _table_ = "client"
        username = Required(str, unique=True)
        info = Optional(str)
        is_active = Required(bool, default=True)

        history = Set(lambda: Storage.ClientHistory)
        contacts = Set(lambda: Storage.ContactsList, reverse="client_id")
        user = Optional(
            lambda: Storage.ContactsList,
        )

    class ClientHistory(db.Entity):
        _table_ = "clients history"
        entry_date = Required(datetime)
        ip_address = Required(str)
        port = Required(int)

        user_id = Required(lambda: Storage.Client)

    class ContactsList(db.Entity):
        _table_ = "contacts list"
        owner_id = Required(lambda: Storage.Client)
        client_id = Required(lambda: Storage.Client)

    def __init__(self):
        self.db.bind(provider="sqlite", filename="db.sqlite3", create_db=True)
        set_sql_debug(True)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def add_user(self, username, info=""):
        client = self.Client(username=username, info=info)

    @db_session
    def get_userlist(self):
        users = self.Client.select(lambda client: client.is_active == True)
        return [user.username for user in users]


if __name__ == "__main__":
    server_db = Storage()
    server_db.add_user(username="Penelope")