from PySide6.QtCore import Signal, QTranslator
from PySide6.QtWidgets import QFormLayout, QGroupBox
from qfluentwidgets.components.widgets import LineEdit

from backend.tools.string_template import StringTemplate
from frontend.widgets.dialog import Dialog
from frontend.widgets.label import Label
from setting.setting_reader import setting


class StringTemplateFillingDialog(Dialog):
    TEMPLATE_FILLED_SIGNAL = Signal(str)

    def __init__(self, template: StringTemplate, parent=None):
        self.template = template
        self.form = QGroupBox()
        self.validation_failed_warning = Label(QTranslator.tr("All fields must be filled."))

        super().__init__(title=QTranslator.tr("Fill the prompt template"), parent=parent)

    def setup_central_layout(self):
        form_layout = QFormLayout()
        for identifier in self.template.get_identifiers():
            form_layout.addRow(Label(text=identifier), LineEdit())
        self.form.setLayout(form_layout)

        self.validation_failed_warning.hide()
        self.validation_failed_warning.setStyleSheet(f"color: {setting.get('SEVERE_WARNING_COLOR')}")

        self.central_layout.addWidget(Label(text=self.template.template))
        self.central_layout.addWidget(self.form)
        self.central_layout.addWidget(self.validation_failed_warning)
        self.central_layout.addWidget(self.button_box)

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


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from backend.tools.string_template import StringTemplate

    app = QApplication(sys.argv)
    template = StringTemplate("Hello, ${name}! You are ${age} years old.")
    dialog = StringTemplateFillingDialog(template)
    dialog.TEMPLATE_FILLED_SIGNAL.connect(print)
    dialog.show()
    sys.exit(app.exec())
