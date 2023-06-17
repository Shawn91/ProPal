from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QApplication, QWidget, QVBoxLayout

from backend.agents.agent_coordinator import LLMCoordinator
from frontend.components.short_text_viewer import ShortTextViewer
from frontend.hotkey_manager import hotkey_manager
from frontend.windows.base import FramelessWindow
from frontend.windows.components.command_text_edit import CommandTextEdit
from setting.setting_reader import setting


class SearchWindow(FramelessWindow):
    WIDTH = 1000  # width of the window

    def __init__(self):
        super().__init__()
        self.hide_shortcut: QShortcut = hotkey_manager.search_window_hide_hotkey.create_shortcut(parent=self)

        # create child widgets
        self.text_edit = CommandTextEdit()
        self.indicator_label = QLabel()
        self.input_container = QWidget()  # contains text edit and indicator label
        self.result_container = QWidget()  # contains search result, ai response, etc.

        self.llm_coordinator = LLMCoordinator()

        self.setup_ui()
        self.connect_hotkey()
        self.connect_signals()

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

    def connect_signals(self):
        self.text_edit.CHAT_SIGNAL.connect(self.chat)
        self.text_edit.textChanged.connect(self.adjust_input_height)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def reset(self):
        self.text_edit.clear()

    def adjust_input_height(self):
        """Adjust the height of the input text edit to fit the content"""
        # get number of lines in the text edit
        line_count = self.text_edit.document().lineCount()
        if line_count > 10:
            line_count = 10
        # get the height of one line
        line_height = self.text_edit.fontMetrics().lineSpacing()
        window_height = line_count * line_height
        self.input_container.setFixedHeight(window_height + 10 + 2 * self.text_edit.PADDING)

    def setup_ui(self):
        # set up the ui of whole window
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.Tool)

        # set up input window geometry
        # move input window to the center of the screen horizontally and 30% from the top vertically
        height = self.text_edit.fontMetrics().lineSpacing() + 10 + 2 * self.text_edit.PADDING
        self.input_container.setFixedSize(self.WIDTH, height)
        screen_geometry = QApplication.instance().primaryScreen().size()
        x = screen_geometry.width() / 2 - self.WIDTH / 2
        y = screen_geometry.height() * setting.get('SEARCH_WINDOW_POSITION_FROM_SCREEN_TOP', 0.3)  # 30% from the top
        self.move(x, y)

        # set up layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.indicator_label)
        input_layout.addWidget(self.text_edit)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_container.setLayout(input_layout)

        global_layout = QVBoxLayout()
        global_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.addWidget(self.input_container)
        global_layout.addWidget(self.result_container)

        self.setLayout(global_layout)

        self.setFixedWidth(self.WIDTH)

    def chat(self, user_input: str):
        result = self.llm_coordinator.coordinate(user_input=user_input)
        text_viewer = ShortTextViewer(text=result.text, text_format='markdown')
        layout = QVBoxLayout()
        layout.addWidget(text_viewer)
        self.result_container.setLayout(layout)
