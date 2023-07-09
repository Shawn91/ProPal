from typing import Tuple, Optional

from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
from qfluentwidgets import PrimaryPushButton, PushButton

from frontend.hotkey_manager import hotkey_manager


class FormDialog(QDialog):
    """title bar is necessary, at least on windows, for a dialog to properly display
    when its parent widget is set to transparent
    """

    def __init__(self, title: str, size: Optional[Tuple[int, int]] = None, accept_text=QTranslator.tr("Confirm"),
                 reject_text=QTranslator.tr("Cancel"), parent=None):
        super().__init__(parent=parent)
        self.central_layout = QVBoxLayout()
        self.title = title
        self.layout = QVBoxLayout()
        self.confirm_button = PrimaryPushButton(accept_text)
        self.cancel_button = PushButton(reject_text)
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(self.confirm_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.setup_central_layout()
        self.setup_ui(size=size)

        shortcut = hotkey_manager.save_hotkey.create_shortcut(self)
        shortcut.activated.connect(self.accept)

    def setup_central_layout(self):
        raise NotImplementedError

    def setup_ui(self, size: Optional[Tuple[int, int]] = None):
        self.setWindowTitle(self.title)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.central_layout)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)
        if size:
            self.setFixedSize(*size)
