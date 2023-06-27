from typing import List

from PySide6.QtCore import QTranslator

from frontend.components.new_prompt import NewPromptDialog


class Command:
    commands = {}  # key is command name; value is command instance
    name: str = ''
    display_name: str = ''

    def execute(self, **kwargs):
        ...


class AddNewPromptCommand(Command):
    name = 'AddNewPrompt'
    display_name = QTranslator.tr("Add New Prompt")

    @staticmethod
    def execute(parent):
        dialog = NewPromptDialog(parent=parent)
        dialog.exec()


class CommandManager:
    def __init__(self):
        # iterate over Command children and add them to self.commands
        self.commands = {}
        for command in Command.__subclasses__():
            self.commands[command.name] = command()

    def search(self, search_str: str) -> List[Command]:
        """Search commands by search_str"""
        return [command for command in self.commands.values() if search_str in command.display_name.lower()]

    @staticmethod
    def execute_command(command: Command, **kwargs):
        """Execute the command"""
        return command.execute(**kwargs)


command_manager = CommandManager()

# class SearchSetting(str, Enum):
#     REGEX = "/re"
#     CASE_SENSITIVE = "/cs"
#
#     @classmethod
#     def has_value(cls, value):
#         return value in cls._value2member_map_
#
#
# class SearchType(str, Enum):
#     PROMPT = "/pr"
#     CHAT_HISTORY = "/ch"
#     FEATURE = "/ft"
#
#     @classmethod
#     def has_value(cls, value):
#         return value in cls._value2member_map_
#
#
# def is_valid_command(command: str) -> bool:
#     """check if the command is valid"""
#     return SearchSetting.has_value(command) or SearchType.has_value(command)
