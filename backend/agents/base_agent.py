"""
An agent is responsible for taking actions in the environment. Every agent is responsible for:
1. taking actions (actions are basic operations like doing regex search, copying text, etc.)
2. coordinating subordinate agents
3. both of the above

An agent takes an input (a trigger that activates it), does some preparation,
check internal state and external environment, takes actions, coordinates subordinate agents, does some clean up,
and finally returns the result.
"""
from typing import Dict, Optional

from backend.models import Error


class BaseTrigger:
    def __init__(self, content):
        self.content = content

    def activate(self, agent: "BaseAgent"):
        """activate an agent"""
        return agent.act(self)

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def to_dict(self):
        raise NotImplementedError


class BaseResult:
    def __init__(
            self,
            trigger: Optional[BaseTrigger] = None,
            content=None,
            success: bool = True,
            error: Optional[Error] = None,
            error_message: str = "",
    ):
        self.trigger = trigger
        self.content = content
        self.success = success
        self.error = error
        self.error_message = error_message

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def to_dict(self):
        raise NotImplementedError


class BaseAgent:
    """This base class is more like an abstract example. It is not meant to be used directly."""

    TRIGGER_CLASS = BaseTrigger
    RESULT_CLASS = BaseResult

    def warm_up(self, trigger_attrs: Dict):
        """Do some preparation before taking actions."""
        trigger = self.TRIGGER_CLASS(**trigger_attrs)
        return trigger, self.RESULT_CLASS(trigger=trigger)

    def introspect(self, trigger, result):
        """check internal states"""
        return result

    def explore(self, trigger, result):
        """explore the external environment"""
        return result

    def do(self, trigger, result):
        """taking actions"""
        return result

    def coordinate_subordinates(self, trigger, result):
        return result

    def cool_down(self, trigger, result):
        """Do some clean up after taking actions, like logging, etc."""
        return result

    def act(self, trigger_attrs: Dict):
        trigger, result = self.warm_up(trigger_attrs=trigger_attrs)
        result = self.introspect(trigger, result)
        result = self.explore(trigger, result)
        result = self.do(trigger, result)
        result = self.coordinate_subordinates(trigger, result)
        result = self.cool_down(trigger, result)
        return result
