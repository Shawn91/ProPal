from numbers import Number
from typing import List, Any

from PySide6.QtCore import Qt, QTranslator, QSize, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QListWidgetItem
from qfluentwidgets import ListWidget

from backend.models import Match
from setting.setting_reader import setting


class TextMatchesSorter:
    @classmethod
    def get_shortest_text_value(cls, values: List[Any]) -> str:
        """get the shortest text of the field that matches the search string"""
        shortest_value = ''
        for value in values:
            if not isinstance(value, str):
                continue
            if isinstance(value, list):
                value = cls.get_shortest_text_value(value)
            if not shortest_value:
                shortest_value = value
            if len(value) < len(shortest_value):
                shortest_value = value
        return shortest_value

    @classmethod
    def score_match(cls, match: Match, search_str: str) -> Number:
        """score a match by the following rules:
        1. TODO: if search_str matches the initials of words in match, give a higher score
        2. the shorter the match text, the higher the score
        """
        text = cls.get_shortest_text_value(match.match_fields_values)
        if not text:
            return 0
        return len(search_str) / len(text)

    @classmethod
    def sort(cls, matches: List[Match], search_str: str) -> List[Match]:
        """sort matches by their similarity to the search string"""
        return sorted(matches, key=lambda x: cls.score_match(x, search_str), reverse=True)


class CommandResultList(ListWidget):
    # TODO: replace the parent of CommandResultList to list view and use custom ListItem to customize ui
    GO_BEYOND_START_OF_LIST_SIGNAL = Signal()

    def __init__(self, matches: List[Match] = None, search_str: str = "", width=1000, parent=None):
        """
        matches is a list of dicts returned by retriever agent result.
            Each element is in the form of {"type": "prompt", "data": Prompt(), "match_fields": ["content", "tag"]}
        """
        super().__init__(parent=parent)
        self.matches = matches if matches else []
        self.search_str = search_str
        self.fixed_width = width
        self.setup_ui()
        if matches:
            self.load_list_items(matches=self.matches, search_str=self.search_str)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Up and self.currentRow() == 0:
            self.GO_BEYOND_START_OF_LIST_SIGNAL.emit()
        else:
            super().keyPressEvent(event)

    def setup_ui(self):
        self.setStyleSheet("background-color:white;")
        self.setFont(setting.default_font)

    def sizeHint(self) -> QSize:
        """set up proper size of the widget to help parent widget determine its proper size"""
        height = self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth()
        return QSize(self.fixed_width, height)

    def reset_widget(self) -> None:
        self.clear()
        self.matches = []
        self.search_str = ""

    def load_list_items(self, matches: List[Match], search_str: str):
        self.reset_widget()
        self.matches = matches
        self.search_str = search_str

        for match in TextMatchesSorter.sort(matches=self.matches, search_str=search_str):
            text = ""
            if match.source == "database":
                text += "    " + match.category.capitalize() + "    " + match.data.content
                if hasattr(match.data, "tags") and match.data.tags:
                    text += "    " + ", ".join(match.data.tags)
            elif match.source == "command":
                text += "    " + "Command" + "    " + match.data.display_name
            item = QListWidgetItem(text, self)
            item.setData(Qt.UserRole, match)
            item.setFont(setting.default_font)

        talk_to_ai_item = QListWidgetItem("    " + QTranslator.tr("Talk to AI") + "    " + self.search_str)
        talk_to_ai_item.setData(Qt.UserRole, Match(category="talk_to_ai"))
        talk_to_ai_item.setFont(setting.default_font)
        if len(self.search_str) > 5:
            self.insertItem(0, talk_to_ai_item)
        else:
            self.addItem(talk_to_ai_item)
        self.setCurrentRow(0)
