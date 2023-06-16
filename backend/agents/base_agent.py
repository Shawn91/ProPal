"""
An agent is responsible for taking actions in the environment. Every agent is responsible for:
1. taking actions (actions are basic operations like doing regex search, copying text, etc.)
2. coordinating subordinate agents
3. both of the above

An agent takes an input (a trigger that activates it), does some preparation,
check internal state and external environment, takes actions, coordinates subordinate agents, does some clean up,
and finally returns the result.
"""
from backend.Error import Error


class BaseTrigger:
    def activate(self, agent: 'BaseAgent'):
        """activate an agent"""
        return agent.act(self)


class BaseResult:
    def __init__(self, success: bool = True, error: Error = None, error_message: str = '', ):
        self.success = success
        self.error = error
        self.error_message = error_message


class BaseAgent:
    """This base class is more like an abstract example. It is not meant to be used directly."""
    RESULT_CLASS = BaseResult
    def warm_up(self, trigger):
        """Do some preparation before taking actions."""
        return self.RESULT_CLASS()

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

    def act(self, trigger: BaseTrigger):
        result = self.warm_up(trigger)
        result = self.introspect(trigger, result)
        result = self.explore(trigger, result)
        result = self.do(trigger, result)
        result = self.coordinate_subordinates(trigger, result)
        result = self.cool_down(trigger, result)
        return result
