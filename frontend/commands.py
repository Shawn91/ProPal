from typing import List

from PySide6.QtCore import QTranslator

from backend.models import Match
from frontend.components.dialogs import NewPromptDialog, LLMConnectionDialog


class Command:
    commands = {}  # key is command name; value is command instance
    name: str = ""
    display_name: str = ""

    def execute(self, **kwargs):
        ...


class AddNewPromptCommand(Command):
    name = "AddNewPrompt"
    display_name = QTranslator.tr("Add New Prompt")

    @staticmethod
    def execute(parent):
        dialog = NewPromptDialog(parent=parent)
        dialog.exec()


class SetProxyCommand(Command):
    name = "SetProxy"
    display_name = QTranslator.tr("Set Proxy")

    @staticmethod
    def execute(parent):
        dialog = LLMConnectionDialog(parent=parent)
        dialog.exec()


class SetOpenAIKeyCommand(Command):
    name = "SetOpenAIKey"
    display_name = QTranslator.tr("Set OpenAI Key")

    @staticmethod
    def execute(parent):
        dialog = LLMConnectionDialog(parent=parent)
        dialog.exec()


class CommandManager:
    def __init__(self):
        # iterate over Command children and add them to self.commands
        self.commands = {}
        for command in Command.__subclasses__():
            self.commands[command.name] = command()

    def search(self, search_str: str) -> List[Match]:
        """Search commands by search_str"""
        raw_matches = [
            command for command in self.commands.values() if search_str.lower() in command.display_name.lower()
        ]
        # search for commands with initials matching search_str
        for command in self.commands.values():
            if command in raw_matches:
                continue
            command_words = command.display_name.lower().split(" ")
            if len(command_words) < len(search_str):
                continue
            if all(
                command_word.startswith(search_char) for search_char, command_word in zip(search_str, command_words)
            ):
                raw_matches.append(command)
        return [
            Match(
                source="command",
                category="command",
                data=x,
                match_fields=["display_name"],
                match_fields_values={"display_name": x.display_name},
            )
            for x in raw_matches
        ]

    @staticmethod
    def execute_command(command: Command, **kwargs):
        """Execute the command"""
        return command.execute(**kwargs)


command_manager = CommandManager()
