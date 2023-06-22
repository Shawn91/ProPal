from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QApplication, QWidget, QVBoxLayout
from qframelesswindow import FramelessWindow

from backend.agents.llm_agent import LLMAgent
from backend.agents.retriever_agent import RetrieverAgent
from frontend.components.search_result_list import SearchResultList
from frontend.components.short_text_viewer import ShortTextViewer
from frontend.hotkey_manager import hotkey_manager

# from frontend.windows.base import FramelessWindow
from frontend.components.command_text_edit import CommandTextEdit
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
        self.llm_agent = LLMAgent()
        self.retriver_agent = RetrieverAgent()

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
        if hasattr(self, "text_edit"):
            self.text_edit.setFocus()

    def connect_hotkey(self):
        # hide or show the window
        hotkey_manager.search_window_hotkey_pressed.connect(self.toggle_visibility)
        self.hide_shortcut.activated.connect(self.hide)

    def connect_signals(self):
        self.text_edit.CHAT_SIGNAL.connect(self.chat)
        self.text_edit.textChanged.connect(self.adjust_input_height)
        self.text_edit.textChanged.connect(self.search)

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
        self.setWindowFlags(self.windowFlags() | Qt.Tool | Qt.WindowStaysOnTopHint)

        # set up input window geometry
        # move input window to the center of the screen horizontally and 30% from the top vertically
        text_edit_height = self.text_edit.fontMetrics().lineSpacing() + 10 + 2 * self.text_edit.PADDING
        self.input_container.setFixedSize(self.WIDTH, text_edit_height)
        screen_geometry = QApplication.instance().primaryScreen().size()
        x = screen_geometry.width() / 2 - self.WIDTH / 2
        y = screen_geometry.height() * setting.get("SEARCH_WINDOW_POSITION_FROM_SCREEN_TOP", 0.3)  # 30% from the top
        self.move(x, y)

        # set up search result container
        self.result_container.setMaximumHeight(screen_geometry.height() * 0.5)

        # set up layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.indicator_label)
        input_layout.addWidget(self.text_edit)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_container.setLayout(input_layout)

        output_layout = QVBoxLayout()
        self.result_container.setLayout(output_layout)

        global_layout = QVBoxLayout()
        global_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.addWidget(self.input_container)
        global_layout.addWidget(self.result_container)
        self.setLayout(global_layout)

        self.setFixedWidth(self.WIDTH)

    def set_widget_in_result_container(self, widget: Optional[QWidget]):
        if widget is None:
            if self.result_container.layout().count() > 0:
                existed_widget = self.result_container.layout().takeAt(0).widget()
                existed_widget.deleteLater()
            self.resize(self.WIDTH, self.input_container.height())
            return
        elif self.result_container.layout().count() > 0:
            existed_widget = self.result_container.layout().takeAt(0).widget()
            self.result_container.layout().replaceWidget(existed_widget, widget)
            existed_widget.deleteLater()
        elif self.result_container.layout().count() == 0:
            self.result_container.layout().addWidget(widget)
        self.resize(self.WIDTH, self.input_container.height() + widget.height() + 10)

    def chat(self, user_input: str):
        result = self.llm_agent.act(trigger_attrs={"content": user_input})
        text_viewer = ShortTextViewer(text=result.content, text_format="markdown")
        self.set_widget_in_result_container(text_viewer)

    def search(self):
        if self.text_edit.toPlainText() == "":
            self.set_widget_in_result_container(widget=None)
            return
        result = self.retriver_agent.act(trigger_attrs={"content": self.text_edit.toPlainText()})
        search_result_list = SearchResultList(data=result.content)
        self.set_widget_in_result_container(search_result_list)
        return result
