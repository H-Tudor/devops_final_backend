import re

from pydantic import BaseModel, Field, field_validator

IMAGE_REGEX = re.compile(
    r"^(?:[a-z0-9._-]+(?:/[a-z0-9._-]+)*)"  # multi-level repo
    r"(?:[:][a-zA-Z0-9._-]+)?$"  # optional tag
)


class ComposeGenerationParameters(BaseModel):
    """
    Docker Compose File generation parameters as expected by ComposeGenerator
    """

    services: list[str] = Field(
        description="""
            Services to deploy as a list or comma-separated string.
            Each service must be provided as 'name:version' with a length of no more than 64
            and with only the following chars: a-z, A-Z, 0-9, [., _, -, :, +] 
            """
    )
    network_name: str = Field(
        max_length=32,
        description="""
            Name of the network the generated docker compose will use 
            The name will have a length of no more than 32 chars and no spaces
            """,
    )
    network_exists: bool
    volume_mount: bool

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
