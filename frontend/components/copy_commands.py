from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout
from qfluentwidgets import ListWidget
from qframelesswindow import FramelessDialog

from backend.tools.markdown_parser import MarkdownParser
from backend.tools.utils import OrderedEnum
from frontend.components.short_text_viewer import ShortTextViewer
from setting.setting_reader import setting


class Commands(str, OrderedEnum):
    COPY_RESPONSE = "Copy Response"
    COPY_CODE_BLOCKS = "Copy Code Blocs"
    COPY_TABLES_AS_CSV = "Copy Tables As CSV"
    COPY_TABLES_AS_MARKDOWN = "Copy Tables As Markdown"


class CopyLLMResponseCommandsDialog(FramelessDialog):
    def __init__(self, target_widget: ShortTextViewer, relative_position="left", parent=None):
        """
        this widget should be displayed alongside the target_widget and controls how to copy content of
            the target_widget
        :param relative_position: "left" or "right" to the target_widget
        """
        super().__init__(parent=parent)
        # hide close button; max and min buttons are already hidden by FramelessDialog
        self.titleBar.closeBtn.hide()

        self.target_widget = target_widget
        self.relative_position = relative_position
        self.command_list = ListWidget()
        self.command_list.itemActivated.connect(self.handle_command_activated)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for command_text in Commands.values():
            item = QListWidgetItem(command_text, self.command_list)
            item.setFont(setting.default_font)
        self.command_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.command_list.setCurrentRow(0)

        layout.addWidget(self.command_list)
        self.setLayout(layout)
        self.setFixedSize(
            self.command_list.sizeHintForColumn(0) + 10, self.command_list.sizeHintForRow(0) * len(Commands.values())
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
        if item.text() == Commands.COPY_RESPONSE:
            clipboard.setText(self.target_widget.raw_text)
        elif item.text() == Commands.COPY_CODE_BLOCKS:
            code_blocks = MarkdownParser.extract_code_blocks(self.target_widget.raw_text)
            clipboard.setText('\n\n'.join(code_blocks))
        elif item.text() == Commands.COPY_TABLES_AS_CSV:
            tables = MarkdownParser.extract_tables(self.target_widget.raw_text, output_format="csv")
            clipboard.setText('\n\n'.join(tables))
        elif item.text() == Commands.COPY_TABLES_AS_MARKDOWN:
            tables = MarkdownParser.extract_tables(self.target_widget.raw_text, output_format="markdown")
            clipboard.setText('\n\n'.join(tables))
        self.close()
