from datetime import datetime
from openai import AsyncOpenAI
from src.configs.config import settings
import logging

logger = logging.getLogger("call_openai")


class OpenAIGenerator():
    """
    Class to interact with OpenAI API.
    
    Attributes:
        model: Model to use for completion
        client: OpenAI client
    """
    
    def __init__(self, llm_model=settings.MODEL_CONF["model_name"], base_url=settings.MODEL_CONF["base_url"], temperature=settings.MODEL_CONF["temperature"]) -> None:
        """
        Initialize OpenAI.
        """

        self.client = AsyncOpenAI(api_key=settings.MODEL_CONF["api_key"], base_url=base_url)  
        self.model = llm_model
        self.temperature = temperature

    async def call_openai(self, messages, **kwargs):
        """
        Asynchronously call OpenAI API.
        """
        try:
            res = await self.client.chat.completions.create( 
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                stream=False,
                **kwargs
            )

            if res.choices:
                answer = res.choices[0].message.content

                usage = {
                    "completion_tokens": res.usage.completion_tokens,
                    "prompt_tokens": res.usage.prompt_tokens,
                    "total_tokens": res.usage.total_tokens,
                    "model": self.model
                }

                if self.model == "gpt-4o-mini":
                    input_price = 0.15
                    output_price = 0.60
                elif self.model == "gpt-4o":
                    input_price = 2.50
                    output_price = 10.00
                else:
                    input_price = 0
                    output_price = 0
                
                total_cost = (usage["prompt_tokens"] / 1_000_000 * input_price) + (usage["completion_tokens"] / 1_000_000 * output_price)

                log_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "completion_tokens": usage["completion_tokens"],
                    "prompt_tokens": usage["prompt_tokens"],
                    "model": self.model.split("/")[-1],
                    "total_cost": round(total_cost, 2)
                }

                logger.info(log_entry)
            return answer
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return None
