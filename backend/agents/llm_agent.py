from enum import Enum
from typing import Dict, Optional

from backend.agents.base_agent import BaseAgent, BaseTrigger, BaseResult
from backend.error import Error
from backend.tools.database import Prompt
from setting.setting_reader import setting


class Model(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"


MODEL_INFO = {Model.GPT_3_5_TURBO: {"provider": "OpenAI", "unit_price_input": 0.0015, "unit_price_output": 0.0002}}


class LLMTrigger(BaseTrigger):
    def __init__(
        self,
        content: str = "",
        model_name=Model.GPT_3_5_TURBO,
        conversation_id: str = "",
        temperature: float = 0.5,
    ):
        super().__init__(content=content)  # input to model
        self.model_name = model_name
        self.conversation_id = conversation_id
        self.history = []  # history of conversation
        self.temperature = temperature

    def to_dict(self):
        return {
            "content": self.content,
            "prompt": {} if self.prompt is None else self.prompt.to_dict(),
            "model_name": self.model_name,
            "conversation_id": self.conversation_id,
            "temperature": self.temperature,
            "history": self.history,
        }


class LLMResult(BaseResult):
    def __init__(
        self,
        trigger: LLMTrigger,
        content: str = "",
        success: bool = True,
        error: Optional[Error] = None,
        error_message: str = "",
    ):
        super().__init__(trigger=trigger, content=content, success=success, error=error, error_message=error_message)
        self.input_token_usage = 0
        self.output_token_usage = 0

    @property
    def cost(self) -> float:
        return (
            self.input_token_usage * MODEL_INFO[self.trigger.model_name]["unit_price_input"]
            + self.output_token_usage * MODEL_INFO[self.trigger.model_name]["unit_price_output"]
        )

    def to_dict(self):
        return {
            "trigger": self.trigger.to_dict() if self.trigger is not None else {},
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "error_message": self.error_message,
            "input_token_usage": self.input_token_usage,
            "output_token_usage": self.output_token_usage,
            "cost": self.cost,
        }


class LLMAgent(BaseAgent):
    import openai

    openai.api_key = setting.get("OPENAI_API_KEY")
    openai.proxy = setting.get("PROXY")

    TRIGGER_CLASS = LLMTrigger
    RESULT_CLASS = LLMResult

    def warm_up(self, trigger_attrs: Dict):
        if trigger_attrs.get("prompt"):
            prompt = self._prepare_prompt(prompt_obj=trigger_attrs["prompt"], user_input=trigger_attrs["user_input"])
        else:
            prompt = trigger_attrs["user_input"]
        trigger = self.TRIGGER_CLASS(content=prompt)
        return trigger, self.RESULT_CLASS(trigger=trigger)

    def do(self, trigger: LLMTrigger, result: LLMResult) -> LLMResult:
        return self.chat(trigger=trigger, result=result)

    def chat(self, trigger: LLMTrigger, result: LLMResult) -> LLMResult:
        try:
            res = self.openai.ChatCompletion.create(
                model=trigger.model_name,
                messages=trigger.history + [{"role": "user", "content": trigger.content}],
                temperature=trigger.temperature,
            )
        except self.openai.error.APIConnectionError:
            return result.set(
                success=False,
                error=Error.API_CONNECTION,
                error_message=f"Connection to {MODEL_INFO[trigger.model_name]} API failed",
            )
        except Exception as e:
            return result.set(success=False, error=Error.UNKNOWN, error_message=str(e))
        return result.set(
            content=res.choices[0].message.content,
            input_token_usage=res.usage.prompt_tokens,
            output_token_usage=res.usage.completion_tokens,
        )

    @staticmethod
    def _prepare_prompt(prompt_obj: Prompt, user_input: str = "", variables: Optional[Dict[str, str]] = None) -> str:
        if variables is None:
            variables = {}
        if "user_input" in prompt_obj.content:
            prompt = prompt_obj.content.format(user_input=user_input, **variables)
        else:
            prompt = prompt_obj.content.format(**variables)
        return prompt


if __name__ == "__main__":
    agent = LLMAgent()
    trigger = LLMTrigger(content="Hello, how are you?")
    print(agent.chat(trigger=trigger, result=LLMResult()))
