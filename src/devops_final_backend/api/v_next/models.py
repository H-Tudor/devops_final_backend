"""vNext API Models Definition

These are pydantic models that both define and validate the API inputs and
return http status 422 if requirements are not met
"""

import re
from typing import Annotated

from pydantic import BaseModel, Field, StrictBool, field_validator

IMAGE_REGEX = re.compile(
    r"^(?:[a-z0-9._-]+(?:/[a-z0-9._-]+)*)"  # multi-level repo
    r"(?:[:][a-zA-Z0-9._-]+)?$"  # optional tag
)


class ComposeGenerationParameters(BaseModel, extra="forbid"):
    """
    Docker Compose File generation parameters as expected by ComposeGenerator
    """

    services: list[Annotated[str, Field(max_length=64, pattern=r"^[a-zA-Z0-9._\-:+]+$")]] = Field(
        ...,
        description="Services to deploy as 'name:version'. Allowed chars: a-z, A-Z, 0-9, [., _, -, :, +].",
        min_length=1,
    )
    network_name: Annotated[str, Field(max_length=32, pattern=r"^\S+$")] = Field(
        ..., description="Name of the network, max 32 chars, no spaces."
    )
    network_exists: StrictBool
    volume_mount: StrictBool

    @classmethod
    @field_validator("services", mode="before")
    def normalize_services(cls, v: list):
        """
        Prevent LLM Injection in the services input
        """
        if not isinstance(v, list):
            raise ValueError("services must be a list")

        for s in v:
            if len(s) > 64 or " " in s:
                raise ValueError(f"Invalid service name: {s}")

            if not IMAGE_REGEX.fullmatch(s):
                raise ValueError(f"Invalid service name: {s}")

        return v

    @classmethod
    @field_validator("network_name", mode="before")
    def normalize_network_name(cls, v: str):
        """
        Prevent LLM Injection in the services input
        """
        if not isinstance(v, str):
            raise ValueError("network name must be a string")

        if len(v) > 32 or " " in v:
            raise ValueError(f"Invalid network name: {v}")

        return v
