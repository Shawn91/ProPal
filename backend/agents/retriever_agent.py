from typing import List, Optional

from backend.agents.base_agent import BaseAgent, BaseResult, BaseTrigger
from backend.tools.database import db_manager


class RetrieverTrigger(BaseTrigger):
    def __init__(self, content=None, sources: Optional[List[str]] = None):
        super().__init__(content=content)
        self.sources = sources if sources else []

    def to_dict(self):
        return {"content": self.content, "sources": self.sources}


class RetrieverResult(BaseResult):
    def __init__(
        self,
        trigger: Optional[RetrieverTrigger] = None,
        content=None,
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
        result.set(content=self.search_db(search_str=trigger.content))
        return result

    def search_db(self, search_str):
        return db_manager.search_by_string(search_str=search_str)
