import threading
import os
import sys
from PyQt6 import QtWidgets

from config.settigs import DB_FILE_NAME
from server.core import Server
from server.models import Storage
from server.gui.server import UiMainWindow


def main():
    db = Storage()
    runner = Server(db=db)

    server = threading.Thread(target=runner.run)
    server.daemon = True
    server.start()

    notificator = threading.Thread(target=runner.status_notify)
    notificator.daemon = True
    notificator.start()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gui = UiMainWindow()
    gui.setupUi(MainWindow)
    gui.users.setModel(gui.get_all_users(db))
    gui.users.resizeColumnsToContents()
    gui.history.setModel(gui.get_all_history(db))
    gui.history.resizeColumnsToContents()
    gui.pushButton.pressed.connect(
        lambda db=db: gui.users.setModel(gui.get_all_users(db))
    )
    gui.pushButton_3.pressed.connect(
        lambda db=db: gui.history.setModel(gui.get_all_history(db))
    )
    gui.get_settings(os.path.join(os.getcwd(), DB_FILE_NAME), runner.sock.getsockname())
    MainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
