import sys
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.centralwidget.setObjectName("centralwidget")
        self.listView = QtWidgets.QListView(parent=self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(10, 30, 190, 410))
        self.listView.setObjectName("listView")
        self.messages = QtGui.QStandardItemModel()
        self.listView_2 = QtWidgets.QListView(parent=self.centralwidget)
        self.listView_2.setGeometry(QtCore.QRect(210, 30, 420, 330))
        self.listView_2.setObjectName("listView_2")
        self.listView_2.setModel(self.messages)
        self.listView_2.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.listView_2.setWordWrap(True)
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(210, 370, 360, 70))
        self.textEdit.setObjectName("textEdit")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(580, 370, 50, 70))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 6, 190, 20))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(210, 0, 420, 30))
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "devChat"))
        self.pushButton.setText(_translate("MainWindow", "Send"))
        self.label.setText(_translate("MainWindow", "Contacts"))
        self.label_2.setText(_translate("MainWindow", "Messages"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.setupUi()
    ui.show()
    sys.exit(app.exec())
