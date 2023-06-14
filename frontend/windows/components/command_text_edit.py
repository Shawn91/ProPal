from enum import Enum

from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPlainTextEdit


class Mode(Enum):
    SEARCH = 0
    CHAT = 1


class SearchSetting(str, Enum):
    REGEX = '/re'
    CASE_SENSITIVE = '/cs'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class SearchType(str, Enum):
    PROMPT = '/pr'
    CHAT_HISTORY = '/ch'
    FEATURE = '/ft'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


def is_valid_command(command: str) -> bool:
    """check if the command is valid"""
    return SearchSetting.has_value(command) or SearchType.has_value(command)


class CommandTextEdit(QPlainTextEdit):
    """A text edit widget that supports search mode and chat mode."""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mode = None
        self.set_mode(Mode.SEARCH)

    def set_mode(self, mode: Mode):
        self.mode = mode
        if self.mode == Mode.SEARCH:
            self.setPlaceholderText(QTranslator.tr(
                "Type to search for prompts or chat histories. Press SPACE to start chatting.",
                type(self).__name__
            ))
            self.viewport().repaint()
        elif self.mode == Mode.CHAT:
            self.setPlaceholderText(QTranslator.tr("Type to chat with AI.", type(self).__name__))
            self.viewport().repaint()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """when user types SPACE, try to recognize the command. Otherwise, pass the event to the base class."""
        text = self.toPlainText()

        if event.key() == Qt.Key_Space:
            # start chatting when user types SPACE in the empty text edit
            if text == "":
                self.set_mode(Mode.CHAT)
                return
            if self.mode == Mode.SEARCH and text.startswith("/"):
                self.set_mode(Mode.SEARCH)
                return
        super().keyPressEvent(event)
