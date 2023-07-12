"""
Запускающий модуль для клиентского приложения.

"""
import sys
from PyQt6 import QtWidgets

from client_app.models import ClientDBase
from client_app.gui.ui_client import MainClientGui
from client_app.core import Client


def main():
    """
    Главная функция запускающего модуля.
    Создает экземпляр клиентского приложения и графическую оболочку.
    Запускает процедуру регистрации или авторизации.
    Создает или загружает из файла ключи безопасности.
    Подключает базу данных.
    """
    app = QtWidgets.QApplication(sys.argv)

    client = Client()
    client.run()
    client.set_username(app)

    db = ClientDBase(client.username)
    client.connect_db(db)
    client.load_keys()

    ui = MainClientGui(db, client)
    ui.start_messaging()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
