import webbrowser

from PySide6.QtCore import QTranslator, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel
from qfluentwidgets import PlainTextEdit, LineEdit

from backend.tools.database import Prompt
from backend.tools.string_template import StringTemplate
from frontend.widgets.dialog import FormDialog
from frontend.widgets.label import Label
from setting.setting_reader import setting


class NewPromptWidget(QWidget):
    def __init__(self, prompt: Prompt = None, parent=None):
        super().__init__(parent=parent)
        self.prompt = prompt
        self.prompt_edit = PlainTextEdit()
        self.tags_edit = LineEdit()
        if prompt:
            self.load_prompt_to_ui()
        self.setup_ui()

    def setup_ui(self):
        self.setFont(setting.default_font)
        self.prompt_edit.setFont(setting.default_font)
        self.tags_edit.setFont(setting.default_font)
        self.prompt_edit.setPlaceholderText(QTranslator.tr("Enter your prompt here"))
        self.tags_edit.setPlaceholderText(QTranslator.tr("Enter tags here separated by comma"))
        self.prompt_edit.setFocus()

        layout = QVBoxLayout()
        layout.addWidget(self.tags_edit)
        layout.addWidget(self.prompt_edit)
        self.setLayout(layout)

    def load_prompt_to_ui(self):
        self.prompt_edit.setPlainText(self.prompt.content)
        # move cursor to the end
        self.prompt_edit.moveCursor(self.prompt_edit.textCursor().End)
        self.tags_edit.setText(",".join(self.prompt.tags))

    def save_prompt(self) -> Prompt:
        if self.prompt:
            self.prompt.content = self.prompt_edit.toPlainText()
            self.prompt.tags = [x.strip() for x in self.tags_edit.text().split(",") if x.strip()]
            self.prompt.save()
        else:
            self.prompt = Prompt(content=self.prompt_edit.toPlainText())
            self.prompt.tags = [x.strip() for x in self.tags_edit.text().split(",") if x.strip()]
            self.prompt.save(force_insert=True)
        return self.prompt


class NewPromptFormDialog(FormDialog):
    def __init__(self, prompt: Prompt = None, parent=None):
        self.new_prompt_widget = NewPromptWidget(prompt=prompt)
        self.validation_failed_warning = Label(QTranslator.tr("You must enter a prompt."))
        title = QTranslator.tr("Edit Prompt") if prompt else QTranslator.tr("New Prompt")
        super().__init__(title=title, size=(500, 300), parent=parent)

    def setup_central_layout(self):
        self.central_layout.addWidget(self.new_prompt_widget)
        self.validation_failed_warning.hide()
        self.validation_failed_warning.setStyleSheet(f"color: {setting.get('SEVERE_WARNING_COLOR')}")
        self.central_layout.addWidget(self.validation_failed_warning)

    def validate(self) -> bool:
        if not self.new_prompt_widget.prompt_edit.toPlainText().strip():
            self.validation_failed_warning.show()
            return False
        return True

    def accept(self) -> None:
        if not self.validate():
            return
        self.new_prompt_widget.save_prompt()
        super().accept()


class LLMConnectionFormDialog(FormDialog):
    def __init__(self, parent=None):
        self.api_key_edit = LineEdit()
        self.api_key_edit.setText(setting.get("OPENAI_API_KEY", default=""))
        self.proxy_edit = LineEdit()
        self.proxy_edit.setText(setting.get("PROXY", default=""))
        super().__init__(title=QTranslator.tr("API Key"), size=(500, 200), parent=parent)

    def setup_central_layout(self):
        self.setFont(setting.default_font)
        self.api_key_edit.setFont(setting.default_font)
        self.api_key_edit.setPlaceholderText(QTranslator.tr("Enter your OPENAI API key here"))
        self.api_key_edit.setFocus()

        self.proxy_edit.setFont(setting.default_font)
        self.proxy_edit.setPlaceholderText(QTranslator.tr("Enter your proxy here"))

        self.central_layout.addWidget(self.api_key_edit)
        self.central_layout.addWidget(self.proxy_edit)

    def accept(self) -> None:
        setting.set(key="OPENAI_API_KEY", value=self.api_key_edit.text())
        setting.set(key="PROXY", value=self.proxy_edit.text())
        super().accept()


class StringTemplateFillingDialog(FormDialog):
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


class NewVersionAvailableDialog(FormDialog):
    def __init__(self, parent=None):
        super().__init__(title=QTranslator.tr("New version available"),
                         accept_text=QTranslator.tr("Get New Version"),
                         reject_text=QTranslator.tr("Later"),
                         parent=parent)

    def setup_central_layout(self):
        self.setFont(setting.default_font)
        message_label = QLabel()
        message_label.setText(QTranslator.tr("A new version of ProPal is available!", type(self).__name__))
        self.central_layout.addWidget(message_label)

    def accept(self) -> None:
        webbrowser.open("https://github.com/Shawn91/ProPal/releases")
        super().accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    new_prompt = NewPromptFormDialog()
    new_prompt.show()
    sys.exit(app.exec())
