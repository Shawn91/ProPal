from PySide6.QtWidgets import QApplication

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
