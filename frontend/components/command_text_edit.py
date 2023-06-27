from enum import Enum

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QTranslator, Signal
from PySide6.QtGui import QKeyEvent
from qfluentwidgets import PlainTextEdit

from setting.setting_reader import setting


class Mode(Enum):
    SEARCH = 0
    TALK = 1


class CommandTextEdit(PlainTextEdit):
    """A text edit widget that supports search mode and chat mode."""

    CONFIRM_SEARCH_SIGNAL = Signal(str)  # signal emitted when user press enter
    CONFIRM_TALK_SIGNAL = Signal(str)

    PADDING = 10  # distance in pixels between border to edit area

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mode = None
        self.set_mode(Mode.SEARCH)

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

        # self.setLineWrapMode(QPlainTextEdit.NoWrap)  # disable line wrap
        # self.setMaximumBlockCount(5)  # make it a single line edit
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # disable vertical scroll bar

    def reset_widget(self):
        self.clear()
        self.enter_search_mode()

    def set_mode(self, mode: Mode):
        self.mode = mode
        self.clear()
        if self.mode == Mode.SEARCH:
            self.setPlaceholderText(
                QTranslator.tr(
                    "Type to search for prompts, chat histories or applications, or start talking to AI.",
                )
            )
            self.viewport().repaint()
        elif self.mode == Mode.TALK:
            self.setPlaceholderText(QTranslator.tr("Type to talk to AI.", type(self).__name__))
            self.viewport().repaint()

    def enter_talk_mode(self):
        self.set_mode(Mode.TALK)

    def enter_search_mode(self):
        self.set_mode(Mode.SEARCH)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """when user types SPACE, try to recognize the command. Otherwise, pass the event to the base class."""
        text = self.toPlainText()
        enter_pressed = event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return
        if enter_pressed and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
            return
        elif enter_pressed:
            if not text.strip():
                return
            if self.mode == Mode.SEARCH:
                self.CONFIRM_SEARCH_SIGNAL.emit(text)
            elif self.mode == Mode.TALK:
                self.CONFIRM_TALK_SIGNAL.emit(text)
            return

        super().keyPressEvent(event)

    def _adjust_height(self):
        """adjust height to fit the content"""
        self.setMinimumHeight(self.fontMetrics().lineSpacing() * self.document().blockCount() + 10 + self.PADDING * 2)
        self.adjustSize()
