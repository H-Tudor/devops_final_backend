import re

from pydantic import BaseModel, Field, field_validator

IMAGE_REGEX = re.compile(
    r"^(?:[a-z0-9._-]+(?:/[a-z0-9._-]+)*)"  # multi-level repo
    r"(?:[:][a-zA-Z0-9._-]+)?$"  # optional tag
)


class ComposeGenerationParameters(BaseModel):
    services: list[str] = Field(
        description="""
            Services to deploy as a list or comma-separated string.
            Each service must be provided as 'name:version' with a length of no more than 64
            and with only the following chars: a-z, A-Z, 0-9, [., _, -, :, +] 
            """
    )
    project: str
    network_name: str
    network_exists: bool
    volume_mount: bool

    @field_validator("services", mode="before")
    def normalize_services(cls, v):
        if not isinstance(v, list):
            raise ValueError("services must be a list")

        for s in v:
            if len(s) > 64 or " " in s:
                raise ValueError(f"Invalid service name: {s}")

            if not IMAGE_REGEX.fullmatch(s):
                raise ValueError(f"Invalid service name: {s}")

        return v
