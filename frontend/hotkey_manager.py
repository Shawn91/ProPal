"""
HotkeyManger holds all the hotkeys used in the application. It reads the hotkeys from the config file.
All windows accept hotkeys from this manager.
"""
from typing import List

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QShortcut, QKeySequence
from pynput.keyboard import GlobalHotKeys, Listener

MODIFIER_KEYS = ['ALT', 'CTRL', 'SHIFT', 'ESC', 'SPACE']


class HotkeyCombination:
    def __init__(self, hotkey_seq: List[str]):
        # make sure all the modifier keys are in upper case
        for idx, key in enumerate(hotkey_seq):
            if key.upper() in MODIFIER_KEYS:
                hotkey_seq[idx] = key.upper()

        self.hotkey_seq = hotkey_seq

    def display(self) -> str:
        return ' + '.join(self.hotkey_seq)

    def for_pynput(self) -> str:
        return '+'.join([f'<{key}>' if key in MODIFIER_KEYS else key for key in self.hotkey_seq])

    def create_shortcut(self, parent=None) -> QShortcut:
        if hasattr(Qt, f"Key_{self.display().capitalize()}"):
            key_sequence = getattr(Qt, f"Key_{self.display().capitalize()}")
        else:
            key_sequence = self.display()
        return QShortcut(QKeySequence(key_sequence), parent)


class HotkeyManager(QObject):
    # activate the search window from any application
    search_window_hotkey = HotkeyCombination(['ALT', 'X'])
    search_window_hotkey_pressed = Signal(bool)

    switch_mode_hotkey = HotkeyCombination(['ESC'])

    global_hotkey_listener: Listener = None

    def __init__(self):
        super().__init__()
        self.init_global_hotkey_listener()

    def init_global_hotkey_listener(self):
        if self.global_hotkey_listener is not None:
            self.global_hotkey_listener.stop()
        global_hotkey_listener = GlobalHotKeys(hotkeys={
            self.search_window_hotkey.for_pynput(): lambda: self.search_window_hotkey_pressed.emit(True)
        })
        global_hotkey_listener.start()


hotkey_manager = HotkeyManager()
