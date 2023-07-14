from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget, QSizePolicy, QListWidget, QVBoxLayout
from qfluentwidgets import ScrollArea

from frontend.components.chat_history_widget import ChatHistoryWidget
from frontend.components.chat_text_edit import ChatTextEdit


class ChatWindow(QWidget):
    WIDTH = 1000
    HEIGHT = 750

    def __init__(self):
        super().__init__()
        self.global_layout = QHBoxLayout(self)
        self.left_panel = ScrollArea()
        self.conversation_list = QListWidget()
        self.right_panel = QWidget()
        self.chat_history_widget = ChatHistoryWidget()
        self.chat_text_edit = ChatTextEdit()
        self._test_ui()
        self.setup_ui()
        self.connect_signals()
        self.chat_text_edit.setFocus()

    def _test_ui(self):
        """TODO: DELETE THIS AFTER DEVELOPMENT"""
        self.left_panel.setStyleSheet('background-color: lightblue;')
        self.conversation_list.setStyleSheet('background-color: yellow;')
        self.conversation_list.addItem('test')

    def setup_ui(self):
        self.global_layout.setSpacing(0)
        self.global_layout.setContentsMargins(0, 0, 0, 0)
        self.global_layout.addWidget(self.left_panel)
        self.global_layout.addWidget(self.right_panel)

        self.left_panel.setWidget(self.conversation_list)
        self.left_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_panel.setFixedWidth(200)
        self.conversation_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.chat_history_widget)
        right_panel_layout.addWidget(self.chat_text_edit)
        self.right_panel.setLayout(right_panel_layout)

        self.setLayout(self.global_layout)

        self.resize(self.WIDTH, self.HEIGHT)

    def connect_signals(self):
        self.chat_text_edit.MESSAGE_SENT_SIGNAL.connect(self.chat_history_widget.add_message)
