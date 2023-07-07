import string

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QFrame
from qfluentwidgets import ListWidget
from qframelesswindow import FramelessDialog

from backend.agents.llm_agent import LLMAgent
from backend.tools.markdown_parser import MarkdownParser
from backend.tools.native_browser_manager import native_browser_manager
from backend.tools.utils import OrderedEnum
from frontend.components.short_text_viewer import ShortTextViewer
from setting.setting_reader import setting


class LLMResponseDialog(FramelessDialog):
    OPEN_BROWSER_SIGNAL = Signal()

    class CopyCommands(str, OrderedEnum):
        COPY_RESPONSE = "Copy Response"
        COPY_CODE_BLOCKS = "Copy Code Blocks"
        COPY_TABLES_AS_CSV = "Copy Tables As CSV"
        COPY_TABLES_AS_MARKDOWN = "Copy Tables As Markdown"

    class SearchCommands(str, OrderedEnum):
        SEARCH_RAW_USER_INPUT = "Search Raw Query"
        SEARCH_REVISED_USER_INPUT = "Search Revised Query"

    def __init__(self, target_widget: ShortTextViewer, user_input: str, relative_position="left", parent=None):
        """
        this widget should be displayed alongside the target_widget
        :param relative_position: "left" or "right" to the target_widget
        :param initial_menu: when the dialog is shown, which menu should be shown first
        """
        super().__init__(parent=parent)
        # hide close button; max and min buttons are already hidden by FramelessDialog
        self.titleBar.closeBtn.hide()
        self.list_widget = ListWidget()
        self.user_input = user_input
        self.target_widget = target_widget
        self.relative_position = relative_position
        self.list_widget.itemActivated.connect(self.handle_command_activated)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        commands = [self.CopyCommands, self.SearchCommands]
        global_idx = 0
        for command_idx, command in enumerate(commands):
            for command_text_idx, command_text in enumerate(command.values()):
                item = QListWidgetItem(f'{string.ascii_uppercase[global_idx]}. {command_text}', self.list_widget)
                item.setFont(setting.default_font)
                global_idx += 1
                assert global_idx < 26, "too many commands"
                item.setData(Qt.UserRole, global_idx)
                # add bottom border to last item
                if command_text_idx == len(command) - 1 and command_idx != len(commands) - 1:
                    border_item = QListWidgetItem(self.list_widget)
                    border_item.setFlags(Qt.NoItemFlags)
                    border_item.setSizeHint(QSize(self.sizeHint().width(), 0))
                    border = QFrame()  # use QFrame to mimic a border
                    border.setFrameShape(QFrame.HLine)
                    self.list_widget.setItemWidget(border_item, border)
        self.list_widget.setCurrentRow(0)

        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.setFixedSize(
            self.list_widget.sizeHintForColumn(0) + 10, self.list_widget.sizeHintForRow(0) * self.list_widget.count()
        )

        # move self to the intended position
        # get position of the target_widget
        target_widget_pos = self.target_widget.mapToGlobal(self.target_widget.pos())
        if self.relative_position == "left":
            self.move(target_widget_pos.x() - self.width() - 10, target_widget_pos.y())
        elif self.relative_position == "right":
            self.move(target_widget_pos.x() + self.target_widget.width() + 10, target_widget_pos.y())
        else:
            raise ValueError(f"relative_position must be either 'left' or 'right', not {self.relative_position}")

    def handle_command_activated(self, item):
        clipboard = QClipboard()
        if self.CopyCommands.has_value(item.text()):
            if item.text() == self.CopyCommands.COPY_RESPONSE:
                clipboard.setText(self.target_widget.raw_text)
            elif item.text() == self.CopyCommands.COPY_CODE_BLOCKS:
                code_blocks = MarkdownParser.extract_code_blocks(self.target_widget.raw_text)
                clipboard.setText("\n\n".join(code_blocks))
            elif item.text() == self.CopyCommands.COPY_TABLES_AS_CSV:
                tables = MarkdownParser.extract_tables(self.target_widget.raw_text, output_format="csv")
                clipboard.setText("\n\n".join(tables))
            elif item.text() == self.CopyCommands.COPY_TABLES_AS_MARKDOWN:
                tables = MarkdownParser.extract_tables(self.target_widget.raw_text, output_format="markdown")
                clipboard.setText("\n\n".join(tables))
        elif self.SearchCommands.has_value(item.text()):
            if item.text() == self.SearchCommands.SEARCH_RAW_USER_INPUT:
                native_browser_manager.search(self.target_widget.raw_text)
            elif item.text() == self.SearchCommands.SEARCH_REVISED_USER_INPUT:
                llm_agent = LLMAgent()
                result = llm_agent.act(
                    trigger_attrs={"stream": False, "user_input": self.user_input, "prompt_name": "REVISE_FOR_SEARCH"}
                )
                native_browser_manager.search(result.content)
            self.OPEN_BROWSER_SIGNAL.emit()
        self.close()
