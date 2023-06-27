from dataclasses import dataclass
from typing import Optional, Any, Literal, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent, QShortcut, QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QApplication, QWidget, QVBoxLayout
from qframelesswindow import FramelessWindow

from backend.agents.llm_agent import LLMAgent
from backend.agents.retriever_agent import RetrieverAgent, Match
from backend.tools.database import Prompt
from frontend.commands import Command
from frontend.components.command_result_list import CommandResultList
# from frontend.windows.base import FramelessWindow
from frontend.components.command_text_edit import CommandTextEdit
from frontend.components.short_text_viewer import ShortTextViewer
from frontend.components.string_template_filling_dialog import StringTemplateFillingDialog
from frontend.hotkey_manager import hotkey_manager
from setting.setting_reader import setting


class CommandWindow(FramelessWindow):
    WIDTH = 1000  # width of the window

    @dataclass
    class TempData:
        type: Literal["text", "image"]  # text, image, file, etc
        data: Any  # text, image binary, file path, etc
        source: str  # source of the data, e.g. "prompt", "clipboard", "user_input", etc

    def __init__(self):
        super().__init__()
        self.hide_shortcut: QShortcut = hotkey_manager.search_window_hide_hotkey.create_shortcut(parent=self)

        # create child widgets
        self.text_edit = CommandTextEdit()
        self.indicator_label = QLabel()
        self.input_container = QWidget()  # contains text edit and indicator label
        self.result_container = QWidget()  # contains search result, ai response, etc.
        self.llm_agent = LLMAgent()
        self.retriever_agent = RetrieverAgent()

        self.setup_ui()
        self.connect_hotkey()
        self.connect_signals()

    @property
    def result_widget(self) -> Optional[Union[CommandResultList, ShortTextViewer]]:
        """return the widget inside the result container"""
        if self.result_container.layout().count() > 0:
            return self.result_container.layout().itemAt(0).widget()
        return None

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

    def connect_signals(self):
        self.text_edit.CONFIRM_SEARCH_SIGNAL.connect(self._execute_search_selection)
        self.text_edit.CONFIRM_TALK_SIGNAL.connect(self._talk_to_ai)
        self.text_edit.textChanged.connect(self._search)
        self.text_edit.textChanged.connect(self._adjust_height)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def reset_widget(self):
        self.text_edit.reset_widget()
        if self.result_widget and hasattr(self.result_widget, "reset_widget"):
            self.result_widget.reset_widget()

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
        self.result_container.setMaximumHeight(screen_geometry.height() * 0.5)

        # set up layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.indicator_label)
        self.indicator_label.hide()
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

    def _adjust_height(self):
        """adjust the height of the window to fit the content"""
        self.input_container.setFixedHeight(self.text_edit.height_by_content + 10)

    def set_widget_in_result_container(self, widget: Optional[QWidget]):
        if widget:
            if self.result_widget:
                existed_item = self.result_container.layout().replaceWidget(self.result_widget, widget)
                existed_widget = existed_item.widget()
                existed_widget.deleteLater()
            else:
                self.result_container.layout().addWidget(widget)
        else:
            if self.result_widget:
                existed_item = self.result_container.layout().takeAt(0)
                existed_widget = existed_item.widget()
                existed_widget.deleteLater()
        self.adjustSize()

    def _execute_search_selection(self):
        text = self.text_edit.toPlainText()
        if text.strip() == "":
            return
        selected_item = self.result_widget.selectedItems()[0]
        match: Match = selected_item.data(Qt.UserRole)
        if match.category == "talk_to_ai":
            self._talk_to_ai()
        elif match.category == "prompt":
            prompt: Prompt = match.data
            if prompt.content_template.is_template:
                dialog = StringTemplateFillingDialog(template=prompt.content_template, parent=self)
                dialog.TEMPLATE_FILLED_SIGNAL.connect(
                    self._wait_for_talking_to_ai
                )
                dialog.exec()
        elif match.category == "command":
            command: Command = match.data
            command.execute(parent=self)

    def _wait_for_talking_to_ai(self, prompt: str):
        self.text_edit.enter_talk_mode()
        self.text_edit.setPlainText(prompt + "\n")
        # move cursor to the end
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)

    def _talk_to_ai(self):
        text = self.text_edit.toPlainText()
        llm_result = self.llm_agent.act(trigger_attrs={"user_input": text})
        text_viewer = ShortTextViewer(text=llm_result.content, text_format="markdown")
        self.set_widget_in_result_container(text_viewer)

    def _search(self):
        text = self.text_edit.toPlainText()
        if text.strip() == "":
            self.set_widget_in_result_container(widget=None)
            return
        result = self.retriever_agent.act(trigger_attrs={"content": text})
        command_result_list = CommandResultList()
        command_result_list.load_list_items(matches=result.content, search_str=text)
        self.set_widget_in_result_container(command_result_list)
        return result