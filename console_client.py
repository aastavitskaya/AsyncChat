import sys
from PyQt6 import QtWidgets

from client.models import ClientDBase
from client.core import Client


def main():
    app = QtWidgets.QApplication(sys.argv)
    client = Client()
    client.run()
    client.set_username(app)
    db = ClientDBase(client.username)
    client.connect_db(db)
    client.main_loop()


if __name__ == "__main__":
    main()
