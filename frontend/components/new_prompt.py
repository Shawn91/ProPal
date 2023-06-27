from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import PlainTextEdit, LineEdit

from backend.tools.database import Prompt
from frontend.widgets.dialog import Dialog
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


class NewPromptDialog(Dialog):
    def __init__(self, prompt: Prompt = None, parent=None):
        self.new_prompt_widget = NewPromptWidget(prompt=prompt)
        title = QTranslator.tr("Edit Prompt") if prompt else QTranslator.tr("New Prompt")
        super().__init__(title=title, size=(500, 300), parent=parent)

    def setup_central_layout(self):
        self.central_layout.addWidget(self.new_prompt_widget)

    def accept(self) -> None:
        self.new_prompt_widget.save_prompt()
        super().accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    new_prompt = NewPromptDialog()
    new_prompt.show()
    sys.exit(app.exec())
