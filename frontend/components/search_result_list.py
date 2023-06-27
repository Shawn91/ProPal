from typing import Dict, List

from PySide6.QtCore import Qt, QTranslator
from PySide6.QtWidgets import QListWidgetItem
from qfluentwidgets import ListWidget

from setting.setting_reader import setting


class SearchResultList(ListWidget):
    # TODO: replace the parent of SearchResultList to list view and use custom ListItem to customize ui

    def __init__(self, matches: List[Dict] = None, search_str: str = "", parent=None):
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

    def sort_matches(self, matches: List[Dict]):
        # TODO: sort matches
        return matches

    def load_list_items(self, matches: List[Dict], search_str: str):
        self.reset_widget()
        self.matches = matches
        self.search_str = search_str

        for match in self.sort_matches(self.matches):
            obj = match.get("data", None)
            if obj and hasattr(obj, "content") and isinstance(obj.content, str):
                text = "    " + match["type"].capitalize() + "    " + obj.content
                if hasattr(obj, "tags") and obj.tags:
                    text += "    " + ", ".join(obj.tags)
                item = QListWidgetItem(text, self)
                item.setData(Qt.UserRole, match)  # store the match info in the item
                item.setFont(self.FONT)

        talk_to_ai_item = QListWidgetItem("    " + QTranslator.tr("Talk to AI") + "    " + self.search_str)
        talk_to_ai_item.setData(Qt.UserRole, {"type": "talk_to_ai"})
        talk_to_ai_item.setFont(self.FONT)
        if len(self.search_str) > 5:
            self.insertItem(0, talk_to_ai_item)
        else:
            self.addItem(talk_to_ai_item)
        self.setCurrentRow(0)
        self.setFixedHeight(self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth())
