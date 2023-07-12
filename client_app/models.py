"""
Модуль, описывающий таблицы и операции над базой данных клиентского приложения.
"""

from datetime import datetime

from pony.orm import Required, Database, set_sql_debug, db_session, delete

from config.settigs import DEBUG, DB_FILE_NAME


class ClientDBase:
    """
    Класс хранилища клиентского приложения.
    :db: (pony.Database) экземпляр базы данных.
    """

    db = Database()

    class Contacts(db.Entity):
        """
        Таблица контактов клиентского приложения.
        :username: (str) имя пользователя.
        :deleted: (bool) статус удаления из контактов.
        """

        username = Required(str, unique=True)
        deleted = Required(bool, default=False)

    class Messages(db.Entity):
        """
        Таблица истории сообщений пользователя.
        :contact: (str) имя пользователя, в переписке с которым находится сообщение.
        :message: (str) тело сообщения.
        :date: (datetime) дата добавления создания сообщения.
        :recieved: (bool) сообщение получен, если истина, иначе отправлено.
        :deleted: (bool) не отображается в переписке, если истина.
        """

        contact = Required(str)
        message = Required(str)
        date = Required(datetime)
        recieved = Required(bool)
        deleted = Required(bool, default=False)

    class AllUsers(db.Entity):
        """
        Таблица всех пользователей зарегистрированных на сервере.
        :username: (str) имя пользователя.
        :is_active: (bool) в настоящий момент активен, если истина.
        :is_contact: (bool) доюавден в контакты, если истина.
        """

        username = Required(str)
        is_active = Required(bool)
        is_contact = Required(bool)

    def __init__(self, name):
        """
        Метод создающий экземпляр клиентской базы данных.
        Создает или подключается к файлу базы данных.
        :name: (str) имя пользователя используется для создания имени файла базы данных.
        """
        self.db.bind(
            provider="sqlite", filename=f"../{name}.{DB_FILE_NAME}", create_db=True
        )
        set_sql_debug(DEBUG)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def add_message(self, contact_username, message, time, recieved=True):
        """
        Метод добавления сообщения в базу данных.
        :contact_username: (str) имя пользователя с которым велась переписка.
        :message: (str) текст сообщения.
        :time: (datetime) дата создания сообщения.
        :recieved: (bool) входящее сообщение, если истина, иначе исходящее.
        """
        store = self.Messages(
            contact=contact_username,
            message=message,
            date=datetime.fromtimestamp(time),
            recieved=recieved,
        )

    @db_session
    def get_users(self):
        """
        Метод возвращающий список всех пользователей зарегистрированных на сервере.
        :return: (list(ClientDBase.AllUsers)) список всех экземпляров класса ClientDBase.AllUsers.
        """
        return self.AllUsers.select()[:]

    @db_session
    def set_users(self, clients):
        """
        Метод обновляющий все записи в таблице ClientDBase.AllUsers в соответствии с
        полученными данными от сервера о пользователях.
        :clients: (list(Storage.Client)) список записей из таблицы пользователей сервера
        с добавлением атрибута is_contact (bool)
        """
        delete(user for user in self.AllUsers.select())
        for client in clients:
            user = self.AllUsers(
                username=client["username"],
                is_active=client["is_active"],
                is_contact=client["is_contact"],
            )

    @db_session
    def update_contacts(self, users_list):
        """
        Метод, обновляющий таблицу контакты на основании полученного списка пользователей с сервера
        Если пользователь больше не в контактах, он помечается удаленным,
        Если есть пользователь, которого нет в контактах, он создается.
        Если есть пользователь, который ранее был удален, он помечается не удаленным.
        При завершении метода на основании новых данных обновляется таблица AllUsers
        :users_list: (list(Storage.ContactsList)) список записей из таблицы контактов сервера.
        """
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
        self.update_all_users()

    @db_session
    def update_all_users(self):
        """
        Метод, обновляющий значение is_contact в таблиц AllUsers на основании данных
        таблицы Contacts.
        """
        contacts = {user.username: user.deleted for user in self.Contacts.select()}
        for user in self.AllUsers.select():
            try:
                user.is_contact = not contacts[user.username]
            except KeyError:
                pass

    @db_session
    def update_messages(self):
        """
        Метод помечает удаленными сообщения из таблицы Messages в случае, если
        контакт из таблицы Contacts помечен удаленным.
        """
        users = [
            user.username for user in self.AllUsers.select() if user.is_contact == True
        ]
        for message in self.Messages.select(lambda mes: mes.contact not in users):
            message.deleted = True

    @db_session
    def get_contacts(self):
        """
        Метод, возвращающий список имен пользователей из таблицы контактов, если пользователь
        не помечен как удаленный.
        :return: (list(str)) список именпользователей.
        """
        return [
            contact.username
            for contact in self.Contacts.select()
            if contact.deleted == False
        ]

    @db_session
    def get_messages(self, username):
        """
        Метод, возвращающий список сообщений от конкретного пользователя,
        если сообщения не помечены как удаленные.
        :username: (str) имя пользователя, чьи сообщения возвращаются.
        :return: list(ClientDBase.Messages) список сообщений.
        """
        return self.Messages.select(
            lambda message: message.contact == username and message.deleted == False
        )[:]


if __name__ == "__main__":
    client_db = ClientDBase("pony")
    client_db.update_contacts(["Alina", "Oleg"])
    client_db.add_message("Alina", "hello", 1680951955.02192)
    client_db.add_message("Oleg", "world", 1680951955.02192)
    client_db.update_contacts(["Alina"])
    client_db.update_messages()
    print(client_db.get_contacts())
    print(client_db.get_messages()[0].message)
