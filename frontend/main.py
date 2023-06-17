import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

if str(Path(__file__).parent.parent.resolve()) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from frontend.hotkey_manager import HotkeyManager
from frontend.windows.search_window import SearchWindow


class MyApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.hotkey_manager = HotkeyManager()
        self.search_window: SearchWindow = SearchWindow()
        self.search_window.show()


if __name__ == "__main__":
    app = MyApp([])
    app.setQuitOnLastWindowClosed(False)
    app.exec()
