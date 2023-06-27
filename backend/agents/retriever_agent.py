from dataclasses import dataclass, field
from typing import List, Optional, Any

from backend.agents.base_agent import BaseAgent, BaseResult, BaseTrigger
from backend.tools.database import db_manager
from frontend.commands import command_manager


class RetrieverTrigger(BaseTrigger):
    def __init__(self, content=None, sources: Optional[List[str]] = None):
        """
        :param sources: limit the search to these sources
        """
        super().__init__(content=content)
        self.sources = sources if sources else []

    def to_dict(self):
        return {"content": self.content, "sources": self.sources}


@dataclass
class Match:
    """one piece of search result"""
    source: str = ''  # database, setting, commands, etc...
    category: str = ''  # prompt, command, etc...
    data: Any = None  # a Prompt instance, a Command instance, etc...
    # what should be displayed in the search result list, e.g. the prompt text, the command name, etc...
    display: Any = None
    # fields that match the search string, e.g. ["name", "description"]
    match_fields: List[str] = field(default_factory=list)


class RetrieverResult(BaseResult):
    def __init__(
            self,
            trigger: Optional[RetrieverTrigger] = None,
            content: List[Match] = None,
            success: bool = True,
            error=None,
            error_message: str = "",
    ):
        super().__init__(trigger=trigger, content=content, success=success, error=error, error_message=error_message)

    def to_dict(self):
        return {
            "trigger": self.trigger.to_dict(),
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "error_message": self.error_message,
        }


class RetrieverAgent(BaseAgent):
    """retrieve data from database, memory, hard disk, or other sources"""

    TRIGGER_CLASS = RetrieverTrigger
    RESULT_CLASS = RetrieverResult

    def do(self, trigger, result):
        result.set(content=self.search(search_str=trigger.content))
        return result

    def search(self, search_str):
        db_matches = [Match(source="database", category=x["category"], data=x["data"], match_fields=x["match_fields"],
                            display=x['data'].content)
                      for x in db_manager.search_by_string(search_str=search_str)]
        command_matches = [Match(source="command", category="command", data=x, match_fields=["display_name"],
                                 display=x.display_name)
                           for x in command_manager.search(search_str=search_str)]
        return db_matches + command_matches

    def _search_db(self, search_str):
        return db_manager.search_by_string(search_str=search_str)
