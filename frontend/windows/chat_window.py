from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget, QSizePolicy, QListWidget, QVBoxLayout
from qfluentwidgets import ScrollArea

from backend.agents.llm_agent import LLMAgent, LLMResult
from frontend.components.chat_history_widget import ChatHistoryWidget
from frontend.components.chat_text_edit import ChatTextEdit
from frontend.windows.base import LLMRequestThread


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
        self.llm_thread = LLMRequestThread(llm_agent=LLMAgent())

        # key is conversation id, value is the latest message widget of that conversation
        self.conversations_latest_message_widgets = {}
        self.active_conversation_id = None
        self._test_ui()
        self.setup_ui()
        self.connect_signals()
        self.chat_text_edit.setFocus()

    def _test_ui(self):
        """TODO: DELETE THIS AFTER DEVELOPMENT"""
        self.left_panel.setStyleSheet('background-color: lightblue;')
        self.conversation_list.setStyleSheet('background-color: yellow;')
        self.conversation_list.addItem('test')
        self.active_conversation_id = '0'

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
        self.chat_text_edit.MESSAGE_WRITTEN_SIGNAL.connect(self.send_message)
        self.llm_thread.content_received.connect(self.update_ai_response)
        self.llm_thread.result_received.connect(self.update_ai_response)

    def send_message(self, message):
        message_widget = self.chat_history_widget.add_message(message, avatar_position='right')
        response_widget = self.chat_history_widget.add_message('...', avatar_position='left')
        self.conversations_latest_message_widgets[self.active_conversation_id] = response_widget
        self.llm_thread.user_input = message
        self.llm_thread.start()

    def update_ai_response(self, response: str | LLMResult):
        response_widget = self.conversations_latest_message_widgets[self.active_conversation_id]
        if isinstance(response, str):
            response_widget.set_message_content(response)
            response_widget.adjustSize()
            response_widget.update()
            response_widget.repaint()
        elif isinstance(response, LLMResult):
            if not response.success:
                response_widget.set_message_content(response.error_message)
            self.conversations_latest_message_widgets.pop(self.active_conversation_id)
        else:
            raise ValueError(f"Unknown type of chunk: {type(response)}")
