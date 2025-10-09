from abc import ABC, abstractmethod
from typing import Any

from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from devops_final_backend.settings import settings

from .errors import InvalidModelParameters
from .models import LLMResponse


class AbstractGenerator(ABC):
    REQUIRED_CONSTANTS = ["MODEL", "TEMPERATURE", "SYSTEM_PROMPT", "TASK_PROMPT_TEMPLATE", "TASK_PROMPT_PARAMS"]
    TEMPERATURE = 0
    SYSTEM_PROMPT = "You are a senior DevOps engineer."
    TASK_PROMPT_TEMPLATE = (
        "Explain the following pipeline: architecture - services - docker compose - helm chart - terraform"
    )
    TASK_PROMPT_PARAMS = []

    @classmethod
    def get_chain(cls) -> Runnable:
        return ChatPromptTemplate.from_messages(
            [("system", cls.SYSTEM_PROMPT), ("user", cls.TASK_PROMPT_TEMPLATE)]
        ) | init_chat_model(
            model=settings.llm_model,
            model_provider=settings.llm_provider,
            api_key=settings.llm_secret,
            temperature=cls.TEMPERATURE,
        )

    @classmethod
    def validate_params(cls, prompt_params: dict[str, Any]) -> bool:
        if not cls.TASK_PROMPT_PARAMS:
            return True

        missing = [k for k in cls.TASK_PROMPT_PARAMS if k not in prompt_params]
        if missing:
            raise InvalidModelParameters(missing)

        return True

    @abstractmethod
    def run(self, prompt_params: dict[str, Any]) -> list[LLMResponse]:
        pass
