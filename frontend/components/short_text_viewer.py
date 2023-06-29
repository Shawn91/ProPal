from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from backend.tools.markdown_parser import MarkdownParser
from setting.setting_reader import setting


class ShortTextViewer(QLabel):
    """A label that shows a short rich/plain text.
    If source text is markdown, it will be converted to html and shown.
    """

    markdown_parser = MarkdownParser(custom_style=f'div, p {{font-size: {setting.get("FONT_SIZE")}px}}')

    def __init__(self, text: str = "", text_format="markdown", parent=None):
        super().__init__(parent=parent)
        self.setup_ui()

        self.text_format = ""
        self.text = ""
        self.set_text(text=text, text_format=text_format)

    def setup_ui(self):
        self.setFont(setting.default_font)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setCursor(Qt.IBeamCursor)
        self.setWordWrap(True)
        self.setStyleSheet(
            """
                background-color: white;
                padding: 10px;
            """
        )

    def set_text(self, text: str, text_format="markdown"):
        self.text = text
        self.text_format = text_format
        if text_format == "markdown":
            self.setText(self.markdown_parser.to_html(self.text))
        else:
            self.setText(text)
