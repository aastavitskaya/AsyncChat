import sys
from PyQt6 import QtCore, QtWidgets, QtGui


class UiDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(300, 200)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(110, 80, 89, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.pressed.connect(self.submit_username)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(20, 40, 261, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 10, 260, 20))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(20, 120, 260, 61))
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Welcome to DevChat"))
        self.pushButton.setText(_translate("Dialog", "Sign in"))
        self.label.setText(_translate("Dialog", "Enter username"))
        self.textBrowser.setHtml(
            _translate(
                "Dialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>',
            )
        )

    def input_username(self, message):
        self.lineEdit.clear()
        self.textBrowser.clear()
        self.textBrowser.insertPlainText(message)
        self.show()

    def submit_username(self):
        if self.lineEdit.text():
            QtWidgets.QApplication.quit()
        else:
            self.textBrowser.clear()
            self.textBrowser.insertPlainText("Usename shouldn't be empty")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = UiDialog()
    ui.setupUi()
    username = "Some text"
    while username:
        ui.input_username(username)
        app.exec()
        username = ui.lineEdit.text()
