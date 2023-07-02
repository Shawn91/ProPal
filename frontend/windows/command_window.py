from enum import Enum
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QHideEvent, QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QApplication, QWidget, QVBoxLayout, QScrollArea
from qframelesswindow import FramelessWindow

from backend.agents.llm_agent import LLMAgent, LLMResult
from backend.agents.retriever_agent import RetrieverAgent
from backend.models import Match
from backend.tools.database import Prompt
from frontend.commands import Command
from frontend.components.command_result_list import CommandResultList
# from frontend.windows.base import FramelessWindow
from frontend.components.command_text_edit import CommandTextEdit
from frontend.components.dialogs import StringTemplateFillingDialog
from frontend.components.short_text_viewer import ShortTextViewer
from frontend.hotkey_manager import hotkey_manager
from setting.setting_reader import setting


class Mode(Enum):
    SEARCH = "search"
    TALK = "talk"
    LLM_RESPONDING = "llm_responding"


class LLMRequestThread(QThread):
    content_received = Signal(str)
    result_received = Signal(LLMResult)

    def __init__(self, llm_agent, user_input: str = ""):
        super().__init__()
        self.llm_agent = llm_agent
        self.user_input = user_input
        self.stop_flag = False  # whether to stop the thread

    def run(self):
        response = self.llm_agent.act(trigger_attrs={"user_input": self.user_input})
        while True:
            if self.stop_flag:
                llm_result = response.send("STOP")  # stop streaming response
                self.result_received.emit(llm_result)
                self.reset()
                break

            try:
                chunk = next(response)
                if isinstance(chunk, str):
                    self.content_received.emit(chunk)
                elif isinstance(chunk, LLMResult):
                    self.result_received.emit(chunk)
            except StopIteration:
                self.reset()
                break

    def reset(self):
        """restore the thread to initial state"""
        self.stop_flag = False
        self.user_input = ""


class CommandWindow(FramelessWindow):
    WIDTH = 1000  # width of the window

    def __init__(self):
        super().__init__()
        self.mode = Mode.SEARCH
        # create child widgets
        self.text_edit = CommandTextEdit()
        self.indicator_label = QLabel()
        self.input_container = QWidget()  # contains text edit and indicator label
        self.result_list = CommandResultList(width=self.WIDTH)  # contains search result
        self.text_viewer = ShortTextViewer()  # contains ai response
        self.result_container = QScrollArea()  # contains search result, ai response, etc.
        self.llm_thread = LLMRequestThread(llm_agent=LLMAgent())
        self.retriever_agent = RetrieverAgent()

        self.result_container_maximum_height = QApplication.instance().primaryScreen().size().height() * 0.5

        self.setup_ui()
        self.connect_hotkey()
        self.connect_signals()

    def hideEvent(self, event: QHideEvent) -> None:
        """override hideEvent to reset the search window when it is hidden"""
        self.reset_widget()
        super().hideEvent(event)

    def show(self):
        """It seems Qt.Tool doesn't accept focus automatically, so we need to manually activate the window.
        This is desirable because we can now do some operations like copying the selected text to the clipboard
            before activate the window.
        """
        self.reset_widget()
        super().show()
        self.activateWindow()
        self.setFocus()
        self.text_edit.setFocus()

    def connect_hotkey(self):
        # hide or show the window
        hotkey_manager.search_window_hotkey_pressed.connect(self.toggle_visibility)
        switch_mode_hotkey = hotkey_manager.switch_mode_hotkey.create_shortcut(parent=self)
        switch_mode_hotkey.activated.connect(self._switch_mode)

    def connect_signals(self):
        self.text_edit.CONFIRM_SIGNAL.connect(self._handle_text_edit_confirm)
        self.text_edit.GO_BEYOND_END_OF_DOCUMENT_SIGNAL.connect(
            lambda: self._move_focus(from_widget=self.text_edit, to_widget=self.result_container)
        )
        self.text_edit.textChanged.connect(self._search)
        self.text_edit.textChanged.connect(self._adjust_height)
        self.result_list.GO_BEYOND_START_OF_LIST_SIGNAL.connect(
            lambda: self._move_focus(from_widget=self.result_list, to_widget=self.text_edit)
        )
        self.result_list.itemActivated.connect(self._execute_search_selection)
        self.llm_thread.content_received.connect(self._update_ai_response)
        self.llm_thread.result_received.connect(self._update_ai_response)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self._switch_mode(to=Mode.SEARCH)
            self.show()

    def reset_widget(self):
        self.text_edit.reset_widget()
        self.text_viewer.reset_widget()
        self.result_list.reset_widget()

    def setup_ui(self):
        # set up the ui of whole window
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.Tool | Qt.WindowStaysOnTopHint)

        # set up input window geometry
        # move input window to the center of the screen horizontally and 30% from the top vertically
        self.input_container.setFixedSize(self.WIDTH, self.text_edit.height_by_content + 10)

        screen_geometry = QApplication.instance().primaryScreen().size()
        x = screen_geometry.width() / 2 - self.WIDTH / 2
        y = screen_geometry.height() * setting.get("SEARCH_WINDOW_POSITION_FROM_SCREEN_TOP", 0.3)  # 30% from the top
        self.move(x, y)

        # set up search result container
        self.result_container.hide()
        self.result_container.setWidgetResizable(True)
        self.result_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_container.setFixedWidth(self.WIDTH)

        # set up layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.indicator_label)
        self.indicator_label.hide()
        input_layout.addWidget(self.text_edit)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_container.setLayout(input_layout)

        global_layout = QVBoxLayout()
        global_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.addWidget(self.input_container)
        global_layout.addWidget(self.result_container)
        self.setLayout(global_layout)

        self.setFixedWidth(self.WIDTH)

    def _handle_text_edit_confirm(self):
        if self.mode == Mode.SEARCH:
            self._execute_search_selection()
        elif self.mode == Mode.TALK:
            self._talk_to_ai()

    def _switch_mode(self, to=None):
        """when to is None, it means stop doing whatever it is doing in the current mode"""
        if to:
            self.mode = to
            for widget in [self.text_edit, self.result_container.widget()]:
                if widget and hasattr(widget, f"enter_{to.value}_mode"):
                    getattr(widget, f"enter_{to.value}_mode")()
        else:
            if self.mode == Mode.LLM_RESPONDING:
                if self.llm_thread.isRunning():
                    # stop the llm if it is running
                    self.llm_thread.stop_flag = True
                    self._switch_mode(to=Mode.TALK)

    def _move_focus(self, from_widget: QWidget, to_widget: QWidget):
        """move focus to the given widget"""
        from_widget.clearFocus()
        if isinstance(to_widget, QScrollArea):
            to_widget = to_widget.widget()
        if to_widget:
            to_widget.setFocus()

    def _adjust_height(self):
        """adjust the height of the window to fit the content"""
        self.input_container.setFixedHeight(self.text_edit.height_by_content + 10)

    def set_widget_in_result_container(self, widget: Optional[QWidget], allow_horizontal_scrollbar: bool = False):
        if widget:
            if self.result_container.widget():
                existed_widget = self.result_container.takeWidget()
                if existed_widget is not widget:
                    existed_widget.reset_widget()
            self.result_container.setWidget(widget)
            self.result_container.show()
            self.result_container.setFixedSize(
                self.WIDTH, min(widget.sizeHint().height(), self.result_container_maximum_height)
            )
            if allow_horizontal_scrollbar and widget.sizeHint().width() > self.WIDTH:
                self.result_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            else:
                self.result_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setFixedWidth(self.WIDTH)
            self.result_container.hide()
            if self.result_container.widget():
                existed_widget = self.result_container.widget()
                existed_widget.reset_widget()
        self.adjustSize()

    def _execute_search_selection(self):
        text = self.text_edit.toPlainText()
        if text.strip() == "":
            return
        selected_item = self.result_container.widget().selectedItems()[0]
        match: Match = selected_item.data(Qt.UserRole)
        if match.category == "talk_to_ai":
            self._switch_mode(to=Mode.TALK)
            self._talk_to_ai()
        elif match.category == "prompt":
            prompt: Prompt = match.data
            if prompt.content_template.is_template:
                dialog = StringTemplateFillingDialog(template=prompt.content_template, parent=self)
                dialog.TEMPLATE_FILLED_SIGNAL.connect(self._wait_for_talking_to_ai)
                dialog.exec()
            else:
                self._wait_for_talking_to_ai(prompt.content)
        elif match.category == "command":
            command: Command = match.data
            command.execute(parent=self)

    def _wait_for_talking_to_ai(self, prompt: str):
        self._switch_mode(to=Mode.TALK)
        self.text_edit.setPlainText(prompt + "\n")
        # move cursor to the end
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)

    def _talk_to_ai(self):
        text = self.text_edit.toPlainText()
        self.set_widget_in_result_container(self.text_viewer, allow_horizontal_scrollbar=True)
        self._switch_mode(to=Mode.LLM_RESPONDING)
        self.llm_thread.user_input = text
        self.llm_thread.start()

    def _update_ai_response(self, response: str | LLMResult):
        if isinstance(response, str):
            self.text_viewer.set_text(response)
            self.result_container.setFixedSize(
                self.WIDTH, min(self.text_viewer.sizeHint().height(), self.result_container_maximum_height)
            )
            self.result_container.repaint()
            self.adjustSize()
        elif isinstance(response, LLMResult):
            # ai response ended
            self._switch_mode(to=Mode.SEARCH)
        else:
            raise ValueError(f"Unknown type of chunk: {type(response)}")

    def _search(self):
        text = self.text_edit.toPlainText()
        if text.strip() == "":
            if self.mode != Mode.SEARCH:
                self._switch_mode(to=Mode.SEARCH)
            self.set_widget_in_result_container(widget=None)
            return
        result = self.retriever_agent.act(trigger_attrs={"content": text})
        self.result_list.load_list_items(matches=result.content, search_str=text)
        self.set_widget_in_result_container(self.result_list)
        return result
