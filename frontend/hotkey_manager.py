"""
HotkeyManger holds all the hotkeys used in the application. It reads the hotkeys from the config file.
All windows accept hotkeys from this manager.
"""
from typing import List

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QShortcut, QKeySequence
from pynput.keyboard import GlobalHotKeys, Listener

MODIFIER_KEYS = ["ALT", "CTRL", "SHIFT", "ESC", "SPACE"]


class HotkeyCombination:
    def __init__(self, hotkey_seq: List[str]):
        self.hotkey_seq = hotkey_seq

    def display(self) -> str:
        return "+".join(self.hotkey_seq)

    def for_pynput(self) -> str:
        return "+".join([f"<{key.upper()}>" if key.upper() in MODIFIER_KEYS else key for key in self.hotkey_seq])

    def create_shortcut(self, parent=None) -> QShortcut:
        return QShortcut(QKeySequence.fromString(self.display()), parent)


class HotkeyManager(QObject):
    # activate the search window from any application
    search_window_hotkey = HotkeyCombination(["ALT", "X"])
    search_window_hotkey_pressed = Signal(bool)

    switch_mode_hotkey = HotkeyCombination(["ESC"])

    save_hotkey = HotkeyCombination(["Ctrl", "Return"])

    delete_hotkey = HotkeyCombination(["Delete"])

    global_hotkey_listener: Listener = None

    def __init__(self):
        super().__init__()
        self.init_global_hotkey_listener()

    def init_global_hotkey_listener(self):
        if self.global_hotkey_listener is not None:
            self.global_hotkey_listener.stop()
        global_hotkey_listener = GlobalHotKeys(
            hotkeys={self.search_window_hotkey.for_pynput(): lambda: self.search_window_hotkey_pressed.emit(True)}
        )
        global_hotkey_listener.start()


hotkey_manager = HotkeyManager()
