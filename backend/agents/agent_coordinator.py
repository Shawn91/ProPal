"""
Every coordinator takes a bunch of Agents (classes, not instances). It takes raw input and creates a trigger
and instances of agents.
"""
from backend.agents.llm_agent import LLMAgent, Model, LLMTrigger


class BaseAgentCoordinator:
    ...


class LLMCoordinator(BaseAgentCoordinator):
    def __init__(self):
        self.llm_agent_class = LLMAgent
        self.output_parsing_agent_class = None

    def coordinate(self, user_input: str, model_name=Model.GPT_3_5_TURBO, conversation_id: str = '',
                   temperature: float = 0.5):
        llm_trigger = LLMTrigger(text=user_input, model_name=model_name, conversation_id=conversation_id,
                                 temperature=temperature)
        llm_agent = self.llm_agent_class()
        llm_result = llm_trigger.activate(llm_agent)
        if self.output_parsing_agent_class:
            output_parser = self.output_parsing_agent_class()
            # transform llm_result to output_parser trigger
            # output_parser_trigger = ...
            # output_parser_result = output_parser_trigger.activate(output_parser)
            # return output_parser_result
            ...
        return llm_result
