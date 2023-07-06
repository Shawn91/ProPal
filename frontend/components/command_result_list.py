from numbers import Number
from typing import List, Any, Iterable

from PySide6.QtCore import Qt, QTranslator, QSize, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QListWidgetItem
from qfluentwidgets import ListWidget

from backend.models import Match
from frontend.hotkey_manager import hotkey_manager
from setting.setting_reader import setting


class TextMatchesSorter:
    @classmethod
    def get_shortest_text_value(cls, values: Iterable[Any]) -> str:
        """get the shortest text of the field that matches the search string"""
        shortest_value = ""
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
        text = cls.get_shortest_text_value(match.match_fields_values.values())
        if not text:
            return 0
        return len(search_str) / len(text)

    @classmethod
    def sort(cls, matches: List[Match], search_str: str) -> List[Match]:
        """sort matches by their similarity to the search string"""
        return sorted(matches, key=lambda x: cls.score_match(x, search_str), reverse=True)


class CommandResultList(ListWidget):
    # TODO: replace the parent of CommandResultList to list view and use custom ListItem to customize ui
    # or use setCellWidget of QTableWidget, or setItemWidget of QListWidget
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
        self.connect_hotkey()
        if matches:
            self.load_list_items(matches=self.matches, search_str=self.search_str)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Up and self.currentRow() == 0:
            self.GO_BEYOND_START_OF_LIST_SIGNAL.emit()
        else:
            super().keyPressEvent(event)

    def connect_hotkey(self):
        delete_hotkey = hotkey_manager.delete_hotkey.create_shortcut(parent=self)
        delete_hotkey.activated.connect(self.delete_prompt)

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
                cutoff_text = match.data.content.replace("\n", "\\n")
                if match.match_positions.get("content"):
                    match_position = match.match_positions["content"][0]
                    center_position = int((match_position[1] - match_position[0]) / 2) + match_position[0]
                    cutoff_text = self._cutoff_text(cutoff_text, center_position=center_position)
                text += "    " + match.category.capitalize() + "    " + cutoff_text

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

    @staticmethod
    def _cutoff_text(text: str, center_position: int) -> str:
        if len(text) < setting.get("MAXIMUM_DISPLAY_LENGTH_IN_SEARCH_RESULT"):
            return text
        half_length = int(setting.get("MAXIMUM_DISPLAY_LENGTH_IN_SEARCH_RESULT") / 2)

        start = max(0, center_position - half_length)
        end = min(len(text), center_position + half_length)
        # if one side is shorter than half of the maximum length, then extend the other side
        if center_position < half_length:
            end = min(len(text), end + half_length - center_position)
        if len(text) - center_position < half_length:
            start = max(0, start - (half_length - (len(text) - center_position)))
        cutoff_text = text[start:end]
        if start > 0:
            cutoff_text = "... " + cutoff_text
        if end < len(text):
            cutoff_text = cutoff_text + " ..."
        return cutoff_text

    def delete_prompt(self):
        if not self.hasFocus():
            return
        item = self.currentItem()
        match = item.data(Qt.UserRole)
        if not match.category == "prompt":
            return
        match.data.delete_instance()
        self.takeItem(self.currentRow())
        self.matches.remove(match)
        self.update()
