from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLabel

from backend.tools.markdown_parser import MarkdownParser
from setting.setting_reader import setting


class ShortTextViewer(QLabel):
    """A label that shows a short rich/plain text.
    If source text is markdown, it will be converted to html and shown.
    """

    markdown_parser = MarkdownParser(
        # somehow, the font size is relatively small in QLabel. So we increase it by 4px
        custom_style=f'div, p {{font-size: {setting.get("FONT_SIZE") + 4}px; '
        f'font-family: {setting.get("FONT_FAMILY")}}};'
    )

    def __init__(self, text: str = "", text_format="markdown", parent=None):
        """

        :param text: could be plain text, html, or markdown
        :param text_format: plaint, markdown, html. this is the format of the text, not what is shown
        """
        super().__init__(parent=parent)
        self.setup_ui()

        self._text_format = ""
        self._text = ""  # not to be confused with self.text(). This is the original text. self.text() is the shown text
        self._html = text if text_format == "html" else ""
        if self._text:
            self.set_text(text=text, text_format=text_format)

    @property
    def raw_text(self):
        return self._text

    @property
    def html(self):
        return self._html

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
        self._text = text
        self._text_format = text_format
        if text_format == "markdown":
            self._html = self.markdown_parser.to_html(self._text)
            self.setText(self._html)
        else:
            if text_format == "html":
                self._html = text
            self.setText(text)
        self.adjustSize()

    def reset_widget(self):
        self.set_text(text="", text_format="html")
        self._html = ""

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # let parent handle ctrl+c when no text is selected
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            if not self.hasSelectedText():
                self.parent().keyPressEvent(event)
                return
        super().keyPressEvent(event)
