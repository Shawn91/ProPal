from PySide6.QtCore import Signal, QTranslator
from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QGroupBox, QDialogButtonBox, QDialog
from qfluentwidgets import PrimaryPushButton, PushButton
from qfluentwidgets.components.widgets import LineEdit

from backend.tools.string_template import StringTemplate
from frontend.widgets.label import Label
from setting.setting_reader import setting


class StringTemplateFillingDialog(QDialog):
    TEMPLATE_FILLED_SIGNAL = Signal(str)

    def __init__(self, template: StringTemplate, parent=None):
        super().__init__(parent=parent)
        self.template = template
        self.form = QGroupBox()
        self.confirm_button = PrimaryPushButton(QTranslator.tr("Confirm"))
        self.cancel_button = PushButton(QTranslator.tr("Cancel"))
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(self.confirm_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.validation_failed_warning = Label(QTranslator.tr("All fields must be filled."))

        self.setup_ui()

    def setup_ui(self):
        form_layout = QFormLayout()
        for identifier in self.template.get_identifiers():
            form_layout.addRow(Label(text=identifier), LineEdit())
        self.form.setLayout(form_layout)

        self.validation_failed_warning.hide()
        self.validation_failed_warning.setStyleSheet(f"color: {setting.get('SEVERE_WARNING_COLOR')}")

        global_layout = QVBoxLayout()
        global_layout.addWidget(Label(text=self.template.template))
        global_layout.addWidget(self.form)
        global_layout.addWidget(self.validation_failed_warning)
        global_layout.addWidget(self.button_box)
        self.setLayout(global_layout)

        self.setWindowTitle(QTranslator.tr("Fill the prompt template"))

    def get_form_data(self):
        data = {}
        for i in range(self.form.layout().rowCount()):
            label = self.form.layout().itemAt(i, QFormLayout.LabelRole).widget()
            line_edit = self.form.layout().itemAt(i, QFormLayout.FieldRole).widget()
            data[label.text()] = line_edit.text().strip()
        return data

    def validate_form(self) -> bool:
        """all fields must be filled"""
        form_data = self.get_form_data()
        if any(not v for v in form_data.values()):
            self.validation_failed_warning.show()
            return False
        return True

    def fill_template(self):
        form_data = self.get_form_data()
        return self.template.substitute(form_data)

    def accept(self) -> None:
        if self.validate_form():
            self.TEMPLATE_FILLED_SIGNAL.emit(self.fill_template())
            super().accept()
