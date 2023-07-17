from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QSpacerItem

from frontend.components.short_text_viewer import ShortTextViewer
from setting.setting_reader import setting


class MessageWidget(QWidget):
    """hold avatar icon, message content, and possibly command buttons"""

    def __init__(self, message, avatar_position='left', parent=None):
        super().__init__(parent=parent)
        if setting.get("AVATAR_SIZE") and setting.get("AVATAR_SIZE") > 0:
            self.avatar = QLabel()
        else:
            self.avatar = None
        self.content_widget = ShortTextViewer(text=message)
        self.avatar_position = avatar_position
        self.setup_ui()
        self._test()

    def _test(self):
        if self.avatar_position == 'left':
            self.setStyleSheet('background-color: pink;')
        else:
            self.setStyleSheet('background-color: lightgreen;')

    def setup_ui(self):
        layout = QHBoxLayout()
        if self.avatar:
            self.avatar.setFixedSize(setting.get("AVATAR_SIZE"), setting.get("AVATAR_SIZE"))
        spacer = QSpacerItem(setting.get("AVATAR_SIZE") + 20, setting.get("AVATAR_SIZE"))
        widgets = [self.avatar, self.content_widget, spacer]
        if self.avatar_position == 'right':
            widgets.reverse()
        for widget in widgets:
            if isinstance(widget, QSpacerItem):
                layout.addSpacerItem(widget)
            else:
                layout.addWidget(widget)
        self.setLayout(layout)

    def set_message_content(self, content):
        self.content_widget.set_text(content)
        # self.adjustSize()


class ChatHistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setup_ui()
        self._test()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignBottom)
        self.setLayout(layout)

    def add_message(self, message, avatar_position='right'):
        input_widget = MessageWidget(message=message, avatar_position=avatar_position)
        self.layout().addWidget(input_widget)
        return input_widget

    def update_content_in_message_widget(self, message_widget, content):
        message_widget.set_message_content(content)
        # self.adjustSize()

    def _test(self):
        messages = ['test']
        for message in messages:
            self.layout().addWidget(MessageWidget(message=message, avatar_position='left'))
