from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent, QShortcut, QFont
from PySide6.QtWidgets import QPlainTextEdit, QHBoxLayout, QLabel, QApplication

from frontend.hotkey_manager import hotkey_manager
from frontend.windows.base import FramelessWindow
from frontend.windows.components.command_text_edit import CommandTextEdit
from setting.setting_reader import setting


class SearchWindow(FramelessWindow):
    FONT_SIZE = setting.get('SEARCH_WINDOW_FONT_SIZE', 18)
    VERTICAL_MARGIN = 10

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.hide_shortcut: QShortcut = hotkey_manager.search_window_hide_hotkey.create_shortcut(parent=self)
        self.layout = QHBoxLayout()
        self.text_edit: QPlainTextEdit = CommandTextEdit()
        self.indicator_label = QLabel()

        self.setup_ui()
        self.connect_hotkey()

    def hideEvent(self, event: QHideEvent) -> None:
        """override hideEvent to reset the search window when it is hidden"""
        self.reset()
        super().hideEvent(event)

    def show(self):
        """It seems Qt.Tool doesn't accept focus automatically, so we need to manually activate the window.
        This is desirable because we can now do some operations like copying the selected text to the clipboard
            before activate the window.
        """
        self.reset()
        super().show()
        self.activateWindow()
        self.setFocus()
        if hasattr(self, 'text_edit'):
            self.text_edit.setFocus()

    def connect_hotkey(self):
        # hide or show the window
        hotkey_manager.search_window_hotkey_pressed.connect(self.toggle_visibility)
        self.hide_shortcut.activated.connect(self.hide)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def reset(self):
        self.text_edit.clear()

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

        # set up window geometry
        # move search window to the center of the screen horizontally and 30% from the top vertically
        height = self.text_edit.fontMetrics().lineSpacing() + 10 + 2 * self.VERTICAL_MARGIN
        width = 1000
        self.setFixedSize(width, height)
        screen_geometry = QApplication.instance().primaryScreen().size()
        x = screen_geometry.width() / 2 - width / 2
        y = screen_geometry.height() * setting.get('SEARCH_WINDOW_POSITION_FROM_SCREEN_TOP', 0.3)  # 30% from the top
        self.move(x, y)

        # set up layout
        self.layout.setContentsMargins(0, self.VERTICAL_MARGIN, 0, self.VERTICAL_MARGIN)
        self.layout.addWidget(self.indicator_label)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
