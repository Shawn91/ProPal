from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent, QShortcut

from frontend.hotkey_manager import hotkey_manager
from frontend.windows.base import FramelessWindow


class SearchWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.hide_shortcut: QShortcut = hotkey_manager.hide_search_window_hotkey.create_shortcut(parent=self)
        self.connect_hotkey()

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
