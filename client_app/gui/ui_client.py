from queue import Queue
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt, pyqtSlot

from PyQt6.QtGui import QStandardItem, QStandardItemModel, QFont
from client_app.gui.client_window import Ui_MainWindow


class Receiver(QObject):
    got_message = pyqtSignal()

    def __init__(self, client):
        super().__init__()
        self.client = client

    @pyqtSlot()
    def receive(self):
        while True:
            try:
                self.client.receive_message()
            except Exception:
                pass
            else:
                self.got_message.emit()


class Transmitter(QObject):
    sent_message = pyqtSignal()

    def __init__(self, client, queue):
        super().__init__()
        self.client = client
        self.queue = queue

    @pyqtSlot()
    def transmit(self):
        while message := self.queue.get():
            self.client.outgoing(message)
            self.queue.task_done()
            self.sent_message.emit()


class MainClientGui(Ui_MainWindow):
    def __init__(self, db, client):
        super().__init__()
        self.db = db
        self.chat = None
        self.client = client
        self.queue = Queue()
        self.setupUi()
        self.listView.doubleClicked.connect(self.select_chat)
        self.pushButton.pressed.connect(self.send_to_user)
        self.pushButton.pressed.connect(self.textEdit.clear)
        self.listView.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.listView.addAction("Add to contacts", self.add_contact)
        self.listView.addAction("Delete from contacts", self.del_contact)
        self.update_users()

    @pyqtSlot()
    def add_contact(self):
        if "👤" in self.listView.currentIndex().data():
            return
        self.queue.put(
            {
                "action": "add_contact",
                "user_id": self.listView.currentIndex().data()[2:-2],
            }
        )

    @pyqtSlot()
    def del_contact(self):
        if "👤" not in self.listView.currentIndex().data():
            return
        self.queue.put(
            {
                "action": "del_contact",
                "user_id": self.listView.currentIndex().data()[2:-2],
            }
        )

    @pyqtSlot()
    def refresh_data(self):
        self.update_users()
        self.update_messages()

    def update_users(self):
        users = self.db.get_users()
        self.users_model = QStandardItemModel()
        for user in users:
            if user.username == self.client.username:
                continue
            active = "🍉" if user.is_active else "💀"
            contact = "👤" if user.is_contact else " "
            username = QStandardItem(f"{active} {user.username} {contact}")
            username.setEditable(False)
            self.users_model.appendRow(username)
        self.listView.setModel(self.users_model)

    def select_chat(self):
        self.chat = self.listView.currentIndex().data()[2:-2]
        self.label_2.setText(f"{self.chat}")
        self.client.request_public_key(self.chat)
        self.update_messages()

    @pyqtSlot()
    def update_messages(self):
        self.db.update_messages()
        contact = self.label_2.text()
        messages = self.db.get_messages(contact)
        self.messages.clear()
        for message in messages:
            text = QStandardItem(f"{message.message}")
            date = QStandardItem(f"{message.date.replace(microsecond=0)}")
            date.setFont(QFont("Helvetica", 6))
            for row in (text, date):
                row.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft
                    if message.recieved == True
                    else Qt.AlignmentFlag.AlignRight
                )
                self.messages.appendRow(row)
        self.listView_2.scrollToBottom()

    def start_messaging(self):
        self.receiver = Receiver(self.client)
        self.receiver.got_message.connect(self.refresh_data)
        self.recv_thread = QThread()
        self.receiver.moveToThread(self.recv_thread)
        self.recv_thread.started.connect(self.receiver.receive)
        self.recv_thread.start()

        self.transmitter = Transmitter(self.client, self.queue)
        self.transmitter.sent_message.connect(self.update_messages)
        self.trans_tread = QThread()
        self.transmitter.moveToThread(self.trans_tread)
        self.trans_tread.started.connect(self.transmitter.transmit)
        self.trans_tread.start()

        self.show()

    def send_to_user(self):
        user_id = self.chat
        message = self.textEdit.toPlainText()
        if not message or not user_id:
            return
        self.queue.put(
            {
                "action": "message",
                "user_id": user_id,
                "body": message,
            }
        )
