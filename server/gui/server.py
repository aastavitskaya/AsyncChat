import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QStandardItem, QStandardItemModel


class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(625, 400)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 20, 600, 350))
        self.tabWidget.setObjectName("tabWidget")
        self.widget = QtWidgets.QWidget()
        self.widget.setAccessibleName("")
        self.widget.setObjectName("widget")
        self.users = QtWidgets.QTableView(parent=self.widget)
        self.users.setGeometry(QtCore.QRect(10, 10, 580, 250))
        self.users.setObjectName("users")
        self.pushButton = QtWidgets.QPushButton(parent=self.widget)
        self.pushButton.setGeometry(QtCore.QRect(500, 280, 90, 25))
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.widget, "")
        self.widget1 = QtWidgets.QWidget()
        self.widget1.setObjectName("widget1")
        self.history = QtWidgets.QTableView(parent=self.widget1)
        self.history.setGeometry(QtCore.QRect(10, 10, 580, 250))
        self.history.setObjectName("history")
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.widget1)
        self.pushButton_3.setGeometry(QtCore.QRect(500, 280, 90, 25))
        self.pushButton_3.setObjectName("pushButton_3")
        self.tabWidget.addTab(self.widget1, "")
        self.widget2 = QtWidgets.QWidget()
        self.widget2.setObjectName("widget2")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.widget2)
        self.lineEdit.setGeometry(QtCore.QRect(200, 50, 360, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.widget2)
        self.lineEdit_2.setGeometry(QtCore.QRect(200, 100, 360, 25))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.widget2)
        self.lineEdit_3.setGeometry(QtCore.QRect(200, 150, 360, 25))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label = QtWidgets.QLabel(parent=self.widget2)
        self.label.setGeometry(QtCore.QRect(50, 50, 460, 30))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.widget2)
        self.label_2.setGeometry(QtCore.QRect(50, 100, 460, 30))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.widget2)
        self.label_3.setGeometry(QtCore.QRect(50, 150, 460, 30))
        self.label_3.setObjectName("label_3")
        self.pushButton_4 = QtWidgets.QPushButton(parent=self.widget2)
        self.pushButton_4.setGeometry(QtCore.QRect(500, 280, 90, 25))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.pressed.connect(QtWidgets.QApplication.quit)
        self.tabWidget.addTab(self.widget2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Server"))
        self.pushButton.setText(_translate("MainWindow", "Refresh"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.widget), _translate("MainWindow", "All users")
        )
        self.pushButton_3.setText(_translate("MainWindow", "Refresh"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.widget1),
            _translate("MainWindow", "Users History"),
        )
        self.label.setText(_translate("MainWindow", "Database path"))
        self.label_2.setText(_translate("MainWindow", "IP address"))
        self.label_3.setText(_translate("MainWindow", "Port"))
        self.pushButton_4.setText(_translate("MainWindow", "Quit"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.widget2), _translate("MainWindow", "Settings")
        )

    def get_all_users(self, db):
        users = db.get_all_users()
        table = QStandardItemModel()
        table.setHorizontalHeaderLabels(["User ID", "Username", "On-line"])
        for user in users:
            user_id, username, is_active = user.id, user.username, user.is_active
            username = QStandardItem(username)
            username.setEditable(False)
            user_id = QStandardItem(str(user_id))
            user_id.setEditable(False)
            is_active = QStandardItem(str(is_active))
            is_active.setEditable(False)
            table.appendRow([user_id, username, is_active])
        return table

    def get_all_history(self, db):
        history = db.get_all_history()
        table = QStandardItemModel()
        table.setHorizontalHeaderLabels(["Username", "Entry date", "IP", "Port"])
        for mem in history:
            user_id, entry_date, ip_address, port = mem

            entry_date = QStandardItem(str(entry_date.replace(microsecond=0)))
            entry_date.setEditable(False)
            user_id = QStandardItem(str(user_id))
            user_id.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            ip_address = QStandardItem(ip_address)
            ip_address.setEditable(False)
            table.appendRow([user_id, entry_date, ip_address, port])
        return table

    def get_settings(self, db_path, ip_config):
        self.lineEdit.insert(db_path)
        self.lineEdit_2.insert(ip_config[0])
        self.lineEdit_3.insert(str(ip_config[1]))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
