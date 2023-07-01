from enum import Enum
from typing import Dict, Optional, Tuple, Iterator

import tiktoken

from backend.agents.base_agent import BaseAgent, BaseTrigger, BaseResult
from backend.models import Error
from setting.setting_reader import setting


class Model(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"


MODEL_INFO = {
    Model.GPT_3_5_TURBO: {
        "provider": "OpenAI",
        "unit_price_input": 0.0015,  # for 1000 tokens
        "unit_price_output": 0.0002,  # for 1000 tokens
        "extra_tokens_per_message": 3,  # openai add 3 extra tokens to every message to format it
        "extra_tokens_for_reply": 3,  # every reply is primed with <|start|>assistant<|message|>, hence the 3 here
    }
}


# class LLMStreamRequest:
#     import openai
#
#     openai.api_key = setting.get("OPENAI_API_KEY")
#     openai.proxy = setting.get("PROXY")
#
#     def __init__(self, cutoff_value: int, model_name: Model, messages: List, temperature: float):
#         """
#         :param cutoff_value: yield results received when num of tokens reach this value
#         """
#         self.cutoff_value = cutoff_value
#         self.model_name = model_name
#         self.messages = messages
#         self.temperature = temperature
#         self.complete_message = ""
#         self.token_encoding = tiktoken.encoding_for_model(self.model_name)
#
#     @property
#     def total_token_usages(self) -> Tuple[int, int]:
#         """see https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
#         for reference
#         """
#         # openai add 3 extra tokens to every message to format it
#         extra_tokens_per_message = 3
#         input_num_tokens = 0
#         for message in self.messages:
#             input_num_tokens += extra_tokens_per_message
#             for key, value in message.items():
#                 input_num_tokens += len(self.token_encoding.encode(value))
#                 if key == "name":
#                     input_num_tokens += 1
#         input_num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>, hence the 3 here
#         output_num_tokens = len(self.token_encoding.encode(self.complete_message))
#         return input_num_tokens, output_num_tokens
#
#     def send(self) -> Iterator[str]:
#         res = self.openai.ChatCompletion.create(
#             model=self.model_name,
#             messages=self.messages,
#             temperature=self.temperature,
#             stream=True,
#         )
#         collected_message = ""
#         for chunk in res:
#             collected_message += chunk["choices"][0]["delta"].get("content", "")  # extract the message
#             if len(self.token_encoding.encode(collected_message)) >= self.cutoff_value:
#                 self.complete_message += collected_message
#                 collected_message = ""
#                 yield self.complete_message
#         if collected_message:
#             self.complete_message += collected_message
#             yield self.complete_message


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
                self.input_token_usage / 1000 * MODEL_INFO[self.trigger.model_name]["unit_price_input"]
                + self.output_token_usage / 1000 * MODEL_INFO[self.trigger.model_name]["unit_price_output"]
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
            prompt = trigger_attrs["prompt"] + "\n" + trigger_attrs["user_input"]
        else:
            prompt = trigger_attrs["user_input"]
        trigger = self.TRIGGER_CLASS(content=prompt)
        return trigger, self.RESULT_CLASS(trigger=trigger)

    def do(self, trigger: LLMTrigger, result: LLMResult):
        return self.chat(trigger=trigger, result=result)

    # @staticmethod
    def chat(self, trigger: LLMTrigger, result: LLMResult, cutoff_value=6) -> Iterator[str | LLMResult]:
        # request = LLMStreamRequest(cutoff_value=5, model_name=trigger.model_name,
        #                            messages=trigger.history + [{"role": "user", "content": trigger.content}],
        #                            temperature=trigger.temperature)
        token_encoding = tiktoken.encoding_for_model(trigger.model_name)
        complete_message = ""
        collected_message = ""
        res = self.openai.ChatCompletion.create(
            model=trigger.model_name,
            messages=trigger.history + [{"role": "user", "content": trigger.content}],
            temperature=trigger.temperature,
            stream=True,
        )
        for chunk in res:
            collected_message += chunk["choices"][0]["delta"].get("content", "")  # extract the message
            if len(token_encoding.encode(collected_message)) >= cutoff_value:
                complete_message += collected_message
                collected_message = ""
                value = yield complete_message
                if value == "STOP":
                    res.close()
                    break
        if collected_message:
            complete_message += collected_message
            yield complete_message
        input_token_usage, output_token_usage = self._calculate_token_usages(
            encoding=token_encoding,
            model_name=trigger.model_name,
            history_messages=trigger.history + [{"role": "user", "content": trigger.content}],
            reply_message=complete_message,
        )
        result.set(
            content=complete_message,
            input_token_usage=input_token_usage,
            output_token_usage=output_token_usage,
        )
        yield result

    @staticmethod
    def _calculate_token_usages(encoding, model_name, history_messages, reply_message) -> Tuple[int, int]:
        """see https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        for reference
        """
        extra_tokens_per_message = MODEL_INFO[model_name].get("extra_tokens_per_message", 0)
        input_num_tokens = 0
        for message in history_messages:
            input_num_tokens += extra_tokens_per_message
            for key, value in message.items():
                input_num_tokens += len(encoding.encode(value))
                if key == "name":
                    input_num_tokens += 1
        input_num_tokens += MODEL_INFO[model_name].get("extra_tokens_for_reply", 0)
        output_num_tokens = len(encoding.encode(reply_message))
        return input_num_tokens, output_num_tokens


if __name__ == "__main__":
    agent = LLMAgent()
    trigger = LLMTrigger(content="count from 1 to 15")
    chat_response = agent.chat(trigger=trigger, result=LLMResult(trigger=trigger))
    while True:
        try:
            chunk = next(chat_response)
            print(chunk, "\n")
            if isinstance(chunk, str):
                if "18" in chunk:
                    chunk = chat_response.send("STOP")
                    assert isinstance(chunk, LLMResult)
                    print("LLMResullt：", chunk.content)
                    print("token usage:", chunk.input_token_usage, chunk.output_token_usage)
                    break
        except:
            print(type(chunk))
            break
