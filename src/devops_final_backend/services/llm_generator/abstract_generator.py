"""Abstract generator from which all inherit"""

from abc import ABC, abstractmethod
from typing import Any

from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from devops_final_backend.settings import settings

from .errors import InvalidModelParameters
from .models import LLMResponse, ResponseType


class AbstractGenerator(ABC):
    """An abstraction of the LLM Generator that contains common or required methods

    Class Constants:

    - TEMPERATURE (int): controls model imagination
    - SYSTEM_PROMPT (str): describes the role assumed by the LLM
    - TASK_PROMPT_TEMPLATE (str): describes the task the LLM will perform with templated slots for runtime variables
    - TASK_PROMPT_PARAMS (list[str]): variables required for the prompt
    - TASK_PROMPT_RETRY (str): templated instruction to use when attempting to regenerate a bad response
    - NO_RESPONSE (list[LLMResponse]): A dummy response list for situations where no generation is wanted
    """

    TEMPERATURE: int = 0
    SYSTEM_PROMPT: str = "You are a senior DevOps engineer."
    TASK_PROMPT_TEMPLATE: str = (
        "Explain the following pipeline: architecture - services - docker compose - helm chart - terraform"
    )
    TASK_PROMPT_PARAMS: list[str] = []
    NO_RESPONSE: list[LLMResponse] = [
        LLMResponse(
            type=ResponseType.NO_RESPONSE,
            name="dummy",
            data="Lorem Ipsum",
        )
    ]

    @classmethod
    def get_chain(cls) -> Runnable:
        """Initializes a chat template, a model and an overall invokeable chain

        Returns:
            Runnable: invokeable LLM entity
        """

        match settings.llm_provider:
            case "ollama":
                chain = init_chat_model(
                    model=settings.llm_model,
                    model_provider=settings.llm_provider,
                    temperature=cls.TEMPERATURE,
                    base_url=settings.llm_base_url,
                )

            case "openai":
                chain = init_chat_model(
                    model=settings.llm_model,
                    model_provider=settings.llm_provider,
                    temperature=cls.TEMPERATURE,
                    api_key=settings.llm_secret,
                )

            case _:
                chain = init_chat_model(
                    model=settings.llm_model,
                    model_provider=settings.llm_provider,
                    temperature=cls.TEMPERATURE,
                )

        return (
            ChatPromptTemplate.from_messages([("system", cls.SYSTEM_PROMPT), ("user", cls.TASK_PROMPT_TEMPLATE)])
            | chain
        )

    @classmethod
    def validate_params(cls, prompt_params: dict[str, Any]):
        """Ensures TASK_PROMPT_PARAMS are present in prompt_params

        Args:
            prompt_params (dict[str, Any]): the runtime prompt params

        Raises:
            InvalidModelParameters: If any expected parameters (as defined in TASK_PROMPT_PARAMS of the child class)
            are missing or invalid. Trigger on child class run() method
        """

        if not cls.TASK_PROMPT_PARAMS:
            return

        missing = [k for k in cls.TASK_PROMPT_PARAMS if k not in prompt_params]
        if missing:
            raise InvalidModelParameters(missing)

        return

    @abstractmethod
    def run(self, prompt_params: dict[str, Any]) -> list[LLMResponse]:
        """LLM Generator interface, ensures the params are sent as a dynamic dictionary

        Args:
            prompt_params (dict[str, Any]): the params

        Returns:
            list[LLMResponse]: the generated files
        """
