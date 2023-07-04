from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QLabel
from qfluentwidgets import ListWidget
from qframelesswindow import FramelessDialog

from backend.tools.utils import OrderedEnum
from setting.setting_reader import setting


class Commands(str, OrderedEnum):
    COPY_RESPONSE = "Copy Response"
    COPY_RESPONSE_AS_HTML = "Copy Response As HTML"
    COPY_ALL_CODE_BLOCKS = "Copy All Code Blocs"
    COPY_ALL_TABLES = "Copy All Tables"


class CopyLLMResponseCommandsDialog(FramelessDialog):
    def __init__(self, target_widget: QLabel, relative_position="left", parent=None):
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
        content = self.target_widget.text()

        self.close()
