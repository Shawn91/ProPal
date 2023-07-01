from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QTranslator, Signal
from PySide6.QtGui import QKeyEvent
from qfluentwidgets import PlainTextEdit

from setting.setting_reader import setting


class CommandTextEdit(PlainTextEdit):
    """A text edit widget that supports search mode and chat mode."""

    CONFIRM_SIGNAL = Signal(str)  # signal emitted when user press enter
    GO_BEYOND_END_OF_DOCUMENT_SIGNAL = Signal()  # signal emitted when user press down arrow key at the last line

    PADDING = 10  # distance in pixels between border to edit area

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.enter_search_mode()
        self.setup_ui()

    @property
    def height_by_content(self):
        """return the height of the widget in pixels
        NOTE: PlainTextEdit.document().size().height() returns line number, not the actual height of the widget.
            TextEdit.document().size().height() returns the actual height of the widget.
        """
        line_count = 1 if self.document().lineCount() == 0 else self.document().lineCount()
        return self.fontMetrics().lineSpacing() * line_count + self.PADDING * 2

    def setup_ui(self):
        self.setFont(setting.default_font)
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(policy)
        self.setStyleSheet(
            f"""
            padding: {self.PADDING}px; 
            background-color:white;
            """
        )

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # disable vertical scroll bar

    def reset_widget(self):
        self.clear()
        self.enter_search_mode()

    def enter_talk_mode(self):
        """user is typing in the message box to talk to AI."""
        self.setReadOnly(False)
        self.setFocus()
        self.setPlaceholderText(QTranslator.tr("Type to talk to AI."))
        self.viewport().repaint()

    def enter_llm_responding_mode(self):
        """llm is responding to user message"""
        self.setReadOnly(True)

    def enter_search_mode(self):
        self.setReadOnly(False)
        self.setFocus()
        self.setPlaceholderText(
            QTranslator.tr(
                "Type to search for prompts, chat histories or applications, or start talking to AI.",
            )
        )
        self.viewport().repaint()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        text = self.toPlainText()
        enter_pressed = event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return
        if enter_pressed and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
            return
        elif enter_pressed:
            if not text.strip():
                return
            self.CONFIRM_SIGNAL.emit(text)
            return
        elif event.key() == Qt.Key_Down:
            # if cursor is already at the last line, emit signal
            if self.textCursor().blockNumber() == self.document().blockCount() - 1:
                self.GO_BEYOND_END_OF_DOCUMENT_SIGNAL.emit()

        super().keyPressEvent(event)

    def _adjust_height(self):
        """adjust height to fit the content"""
        self.setMinimumHeight(self.fontMetrics().lineSpacing() * self.document().blockCount() + 10 + self.PADDING * 2)
        self.adjustSize()
