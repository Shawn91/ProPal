from typing import Dict, List

from PySide6.QtWidgets import QTreeWidgetItem, QListWidgetItem, QLabel, QWidget, QHBoxLayout, QListWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from qfluentwidgets import TreeWidget, ListWidget

from setting.setting_reader import setting


class SearchResultList(ListWidget):
    # TODO: replace the parent of SearchResultList to list view and use custom ListItem to customize ui
    def __init__(self, matches: List[Dict], search_str: str = "", parent=None):
        """
        matches is a list of dicts returned by retriever agent result.
            Each element is in the format of {"type": "prompt", "data": Prompt(), "match_fields": ["content", "tag"]}
        """
        super().__init__(parent=parent)
        self.setup_ui()
        self.matches = matches
        self.search_str = search_str
        self.load_list_items()

    def setup_ui(self):
        self.setStyleSheet("background-color:white;")

    def sort_matches(self, matches: List[Dict]):
        # TODO: sort matches
        return matches

    def load_list_items(self):
        font = QFont()
        font.setPointSize(setting.get("FONT_SIZE"))

        for match in self.sort_matches(self.matches):
            object = match.get("data", None)
            if object and hasattr(object, "content") and isinstance(object.content, str):
                text = "\t" + match["type"].capitalize() + "\t" + object.content
                if hasattr(object, "tag_list") and object.tag_list:
                    text += "\t" + ", ".join(object.tag_list)
                item = QListWidgetItem(text, self)
                item.setData(Qt.UserRole, match)  # store the match info in the item
                item.setFont(font)

        talk_to_ai_item = QListWidgetItem("\t" + self.tr("Talk to AI") + "\t" + self.search_str)
        talk_to_ai_item.setData(Qt.UserRole, {"type": "talk_to_ai", "data": self.search_str})
        talk_to_ai_item.setFont(font)
        if len(self.search_str) > 5:
            self.insertItem(0, talk_to_ai_item)
        else:
            self.addItem(talk_to_ai_item)

        self.setCurrentRow(0)
        self.setFixedHeight(self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth())
