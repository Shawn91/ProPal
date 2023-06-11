from PySide6.QtCore import QObject, Signal
from pynput.keyboard import GlobalHotKeys, Listener


# activate the search window from any application
search_window_hotkey = '<alt>+x'


class HotkeyManager(QObject):
    search_window_hotkey_pressed = Signal(bool)

    global_hotkey_listener: Listener = None

    def __init__(self):
        super().__init__()
        self.init_global_hotkey_listener()

    def init_global_hotkey_listener(self):
        if self.global_hotkey_listener is not None:
            self.global_hotkey_listener.stop()
        global_hotkey_listener = GlobalHotKeys(hotkeys={
            search_window_hotkey: lambda: self.search_window_hotkey_pressed.emit(True)
        })
        global_hotkey_listener.start()
