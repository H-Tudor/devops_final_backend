from enum import Enum, auto

from pydantic import BaseModel


class ResponseType(Enum):
    COMPOSE_FILE = auto()
    ENV_FILE = auto()


class LLMResponse(BaseModel):
    type: ResponseType
    name: str
    data: str
