from typing import List

from PySide6.QtCore import Qt, QTranslator
from PySide6.QtWidgets import QListWidgetItem
from qfluentwidgets import ListWidget

from backend.agents.retriever_agent import Match
from setting.setting_reader import setting


class CommandResultList(ListWidget):
    # TODO: replace the parent of CommandResultList to list view and use custom ListItem to customize ui

    def __init__(self, matches: List[Match] = None, search_str: str = "", parent=None):
        """
        matches is a list of dicts returned by retriever agent result.
            Each element is in the form of {"type": "prompt", "data": Prompt(), "match_fields": ["content", "tag"]}
        """
        super().__init__(parent=parent)
        self.matches = matches if matches else []
        self.search_str = search_str
        self.setup_ui()
        if matches:
            self.load_list_items(matches=self.matches, search_str=self.search_str)

    def setup_ui(self):
        self.setStyleSheet("background-color:white;")
        self.setFont(setting.default_font)

    def reset_widget(self) -> None:
        self.clear()
        self.matches = []
        self.search_str = ""

    def sort_matches(self, matches: List[Match]):
        # TODO: sort matches
        return matches

    def load_list_items(self, matches: List[Match], search_str: str):
        self.reset_widget()
        self.matches = matches
        self.search_str = search_str

        for match in self.sort_matches(self.matches):
            text = ''
            if match.source == "database":
                text += "    " + match.category.capitalize() + "    " + match.display
                if hasattr(match.data, "tags") and match.data.tags:
                    text += "    " + ", ".join(match.data.tags)
            elif match.source == "command":
                text += "    " + "Command" + "    " + match.display
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
        self.setFixedHeight(self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth())
