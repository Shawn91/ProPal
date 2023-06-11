from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent, QShortcut, QFont
from PySide6.QtWidgets import QPlainTextEdit, QHBoxLayout, QLabel

from frontend.hotkey_manager import hotkey_manager
from frontend.windows.base import FramelessWindow


class SearchWindow(FramelessWindow):
    FONT_SIZE = 18
    VERTICAL_MARGIN = 10

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.hide_shortcut: QShortcut = hotkey_manager.hide_search_window_hotkey.create_shortcut(parent=self)
        self.connect_hotkey()
        self.layout = QHBoxLayout()
        self.text_edit: QPlainTextEdit = QPlainTextEdit()
        self.indicator_label = QLabel()
        self.setup_ui()

    def hideEvent(self, event: QHideEvent) -> None:
        """override hideEvent to clear the search window when it is hidden"""
        self.clear()
        super().hideEvent(event)

    def show(self):
        """It seems Qt.Tool doesn't accept focus automatically, so we need to manually activate the window.
        This is desirable because we can now do some operations like copying the selected text to the clipboard
            before activate the window.
        """
        super().show()
        self.activateWindow()
        self.setFocus()

    def connect_hotkey(self):
        hotkey_manager.search_window_hotkey_pressed.connect(self.show)
        self.hide_shortcut.activated.connect(self.hide)

    def clear(self):
        ...

    def adjust_height(self):
        """Adjust the height of the window to fit the content"""
        # get number of lines in the text edit
        line_count = self.text_edit.document().lineCount()
        # get the height of one line
        line_height = self.text_edit.fontMetrics().lineSpacing()
        window_height = line_count * line_height
        self.setFixedHeight(window_height + 10 + 2 * self.VERTICAL_MARGIN)

    def setup_ui(self):
        # set up the text edit
        font = QFont()
        font.setPointSize(self.FONT_SIZE)
        self.text_edit.setFont(font)
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.text_edit.setSizePolicy(policy)
        self.text_edit.document().contentsChanged.connect(self.adjust_height)

        # TODO: set window geometry

        self.layout.setContentsMargins(0, self.VERTICAL_MARGIN, 0, self.VERTICAL_MARGIN)
        self.layout.addWidget(self.indicator_label)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
        self.setFixedHeight(self.text_edit.fontMetrics().lineSpacing() + 10 + 2 * self.VERTICAL_MARGIN)
        self.setFixedWidth(1000)
