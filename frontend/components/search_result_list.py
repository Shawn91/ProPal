from typing import Dict, List
from PySide6.QtWidgets import QTreeWidgetItem, QListWidgetItem, QLabel, QWidget, QHBoxLayout, QListWidget
from qfluentwidgets import TreeWidget, ListWidget

from backend.tools.database import Prompt


# TODO: replace the parent of SearchResultList to list view and use this ListItem to customize ui
class ListItem(QWidget):
    def __init__(self, data: List[str]):
        super().__init__()
        self.data = data
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        for item in self.data:
            label = QLabel(item)
            layout.addWidget(label)
        self.setLayout(layout)


class SearchResultList(ListWidget):
    def __init__(self, data: Dict, parent=None):
        """data is a dict returned by retriever agent result with slight modification"""
        super().__init__(parent=parent)
        self.setup_ui()
        self.data = data
        self.load_list_items()

    def setup_ui(self):
        self.setStyleSheet("background-color:white;")

    def load_list_items(self):
        # prompt_match is in the format of [{"data": Prompt(), "match_type": ["content", "tag"]}]
        for prompt_match in self.data.get("prompt", []):
            prompt = prompt_match["data"]
            QListWidgetItem("\t" + "Prompt" + "\t" + prompt.content + "\t" + ", ".join(prompt.tag_list), self)
        self.setCurrentRow(0)
        self.setFixedHeight(self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth())
