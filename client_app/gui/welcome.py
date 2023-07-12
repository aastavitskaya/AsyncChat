import sys
from PyQt6 import QtCore, QtWidgets, QtGui


class UiDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(300, 230)
        self.new_user = False
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(20, 120, 121, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.pressed.connect(self.sign_in)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(20, 30, 261, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 10, 260, 20))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.lineEdit_2 = QtWidgets.QLineEdit(self)
        self.lineEdit_2.setGeometry(QtCore.QRect(20, 80, 261, 25))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(158, 120, 121, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.pressed.connect(self.register)
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(20, 160, 260, 60))
        self.textBrowser.setObjectName("textBrowser")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 260, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Welcome to DevChat"))
        self.pushButton.setText(_translate("Dialog", "Sign in"))
        self.label.setText(_translate("Dialog", "Enter username"))
        self.pushButton_2.setText(_translate("Dialog", "Register"))
        self.label_2.setText(_translate("Dialog", "Enter password"))

    def input_username(self, message):
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.textBrowser.clear()
        self.textBrowser.insertPlainText(message)
        self.show()

    def sign_in(self):
        self.new_user = False
        if self.lineEdit.text() and self.lineEdit_2.text():
            QtWidgets.QApplication.quit()
        else:
            self.textBrowser.clear()
            self.textBrowser.insertPlainText("Usename and password shouldn't be empty")

    def register(self):
        self.sign_in()
        self.new_user = True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = UiDialog()
    ui.setupUi()
    username = "admin"
    password = "admin"
    while username:
        ui.input_username(f"u:{username}\np:{password}")
        app.exec()
        username = ui.lineEdit.text()
        password = ui.lineEdit.text()
