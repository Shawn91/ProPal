import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from frontend.components.dialogs import LLMConnectionDialog
from setting.setting_reader import setting

if str(Path(__file__).parent.parent.resolve()) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from frontend.hotkey_manager import HotkeyManager
from frontend.windows.command_window import CommandWindow


class MyApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.hotkey_manager = HotkeyManager()
        self.search_window: CommandWindow = CommandWindow()
        self.initial_checks()
        self.search_window.show()

    @staticmethod
    def initial_checks():
        if not setting.get("OPENAI_API_KEY"):
            LLMConnectionDialog().exec()


if __name__ == "__main__":
    app = MyApp([])
    app.setQuitOnLastWindowClosed(False)
    app.exec()
