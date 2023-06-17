from enum import Enum

from backend.agents.base_agent import BaseAgent, BaseTrigger, BaseResult
from backend.error import Error
from setting.setting_reader import setting


class Model(str, Enum):
    GPT_3_5_TURBO = 'gpt-3.5-turbo'


MODEL_INFO = {
    Model.GPT_3_5_TURBO: {
        'provider': 'OpenAI',
        'unit_price_input': 0.0015,
        'unit_price_output': 0.0002
    }
}


class LLMTrigger(BaseTrigger):
    def __init__(self, text: str, model_name=Model.GPT_3_5_TURBO, conversation_id: str = '', temperature: float = 0.5):
        self.text = text  # input to model
        self.model_name = model_name
        self.conversation_id = conversation_id
        self.history = []  # history of conversation
        self.temperature = temperature


class LLMResult(BaseResult):
    def __init__(self, success: bool = True, error_message: str = '', model_name: Model = Model.GPT_3_5_TURBO,
                 text: str = ''):
        super().__init__(success=success, error_message=error_message)
        self.model_name = model_name
        self.text = text  # output from model
        self.input_token_usage = 0
        self.output_token_usage = 0

    @property
    def cost(self) -> float:
        return self.input_token_usage * MODEL_INFO[self.model_name]['unit_price_input'] + \
            self.output_token_usage * MODEL_INFO[self.model_name]['unit_price_output']


class LLMAgent(BaseAgent):
    import openai
    openai.api_key = setting.get("OPENAI_API_KEY")
    openai.proxy = setting.get('PROXY')

    RESULT_CLASS = LLMResult

    def warm_up(self, trigger: LLMTrigger):
        return self.RESULT_CLASS(model_name=trigger.model_name)

    def do(self, trigger: LLMTrigger, result: LLMResult) -> LLMResult:
        return self.chat(trigger=trigger, result=result)

    def chat(self, trigger: LLMTrigger, result: LLMResult) -> LLMResult:
        try:
            res = self.openai.ChatCompletion.create(
                model=trigger.model_name,
                messages=trigger.history + [{'role': 'user', "content": trigger.text}],
                temperature=trigger.temperature,
            )
        except self.openai.error.APIConnectionError:
            return result.set(success=False, error=Error.API_CONNECTION,
                              error_message=f'Connection to {MODEL_INFO[trigger.model_name]} API failed')
        except Exception as e:
            return result.set(success=False, error=Error.UNKNOWN, error_message=str(e))
        return result.set(text=res.choices[0].message.content, input_token_usage=res.usage.prompt_tokens,
                          output_token_usage=res.usage.completion_tokens)


if __name__ == "__main__":
    agent = LLMAgent()
    trigger = LLMTrigger(text="Hello, how are you?")
    print(agent.chat(trigger=trigger, result=LLMResult()))
