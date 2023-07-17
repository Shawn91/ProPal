from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics, QKeyEvent
from PySide6.QtWidgets import QTextEdit, QApplication

from setting.setting_reader import setting


class ChatTextEdit(QTextEdit):
    MESSAGE_WRITTEN_SIGNAL = Signal(str)

    def __init__(self, initial_line_num=5, parent=None):
        super().__init__(parent=parent)
        self.initial_line_num = initial_line_num  # number of lines to show initially
        self.setup_ui()
        self.document().contentsChanged.connect(self.set_height_by_content)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.NoModifier and (
                event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            self.send_message()
            return
        super().keyPressEvent(event)

    def setup_ui(self):
        self.setFont(setting.default_font)
        self.set_height_by_line_number(line_number=self.initial_line_num)

    def send_message(self):
        self.MESSAGE_WRITTEN_SIGNAL.emit(self.toPlainText())
        self.clear()

    def set_height_by_line_number(self, line_number):
        line_height = QFontMetrics(self.font()).lineSpacing()
        margins = self.contentsMargins()
        document_margin = self.document().documentMargin()
        height = line_number * line_height + (margins.top() + margins.bottom()) + \
                 (document_margin + self.frameWidth()) * 2
        self.setFixedHeight(height)

    def set_height_by_content(self):
        if self.document().blockCount() < self.initial_line_num:
            self.set_height_by_line_number(line_number=self.initial_line_num)
            return
        margins = self.contentsMargins()
        document_height = self.document().documentLayout().documentSize().height()
        height = document_height + margins.top() + margins.bottom() + self.frameWidth() * 2
        self.setFixedHeight(height)
