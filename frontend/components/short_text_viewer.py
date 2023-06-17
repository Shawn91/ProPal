from PySide6.QtWidgets import QLabel
from markdown import markdown


class ShortTextViewer(QLabel):
    """A label that shows a short rich/plain text.
    If source text is markdown, it will be converted to html and shown.
    """

    def __init__(self, text: str, text_format='markdown', parent=None):
        super().__init__(parent=parent)
        self.text_format = text_format
        self.text = text
        if text_format == "markdown":
            self.setText(markdown(text))
        else:
            self.setText(text)
        self.setStyleSheet("background-color: white;")
