import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from frontend.windows.chat_window import ChatWindow
from setting.setting_reader import setting

if str(Path(__file__).parent) not in sys.path:
    sys.path.append(str(Path(__file__).parent))

from frontend.utils import NewVersionChecker
from frontend.components.form_dialogs import NewVersionAvailableDialog, LLMConnectionFormDialog
from frontend.hotkey_manager import HotkeyManager

new_version_checker = NewVersionChecker()


class MyApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.hotkey_manager = HotkeyManager()
        # self.search_window: CommandWindow = CommandWindow()
        self.chat_window = ChatWindow()
        self.initial_checks()
        # self.search_window.show()
        self.chat_window.show()
        # self.chat_window.chat_text_edit.setFocus()

    @staticmethod
    def initial_checks():
        if not setting.get("OPENAI_API_KEY"):
            LLMConnectionFormDialog().exec()

    @staticmethod
    def show_new_version_dialog():
        NewVersionAvailableDialog().exec()


app = MyApp([])
app.setQuitOnLastWindowClosed(False)
new_version_checker.NEW_VERSION_AVAILABLE.connect(app.show_new_version_dialog)

new_version_checker.start()
app.exec()
