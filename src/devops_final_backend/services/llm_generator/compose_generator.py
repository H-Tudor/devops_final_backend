from typing import Any

from yaml import YAMLError, safe_dump, safe_load

from .abstract_generator import AbstractGenerator
from .errors import InvalidModelResponse, ModelFailedToRespond, ValidationError
from .models import LLMResponse, ResponseType


class ComposeGenerator(AbstractGenerator):
    TEMPERATURE = 0
    SYSTEM_PROMPT = """
    You are a senior DevOps engineer.
    Always generate valid configuration files exactly in the requested format.
    Do not include comments, explanations, or extra text.
    Use the latest official image for the specified software and version
    For each configuration, create or use a dedicated Docker network as indicated.
    """
    TASK_PROMPT_TEMPLATE = """
    Generate a valid Docker Compose YAML configuration without anything else like code blocks.
    Always include a 'networks' section defining network '{network_name}'.
    Each service must explicitly reference this network.
    Use or create this network according to: {network_exists}.
    Deploy the following services: {services} at the specified versions with
    any additional dependent services required at latest major version known if not specified.
    Declare all required volumes in the volumes section, and map each declared volume to {volume_mount} using named volume references.
    {additional_instructions}
    """
    TASK_PROMPT_PARAMS = ["project", "network_name", "network_exists", "services", "volume_mount"]
    TASK_PROMPT_RETRY = "The previous configuration was invalid because {error}. Regenerate the entire YAML"

    def __init__(self):
        super().__init__()
        self.env_store: dict[str, dict] = {}

    def run(self, prompt_params: dict[str, Any]) -> list[LLMResponse]:
        result = []
        self.validate_params(prompt_params)
        self.assign_param_defaults(prompt_params)
        resp = self.get_chain().invoke(prompt_params)

        if not resp or not resp.text():
            raise ModelFailedToRespond()

        try:
            parsed_data = self.parse_compose_config(resp.text())
        except ValidationError as err:
            if prompt_params.get("retry", False):
                raise InvalidModelResponse(err.message)

            prompt_params["retry"] = True
            prompt_params["error"] = err.message
            return self.run(prompt_params)

        result = [
            LLMResponse(
                type=ResponseType.ENV_FILE,
                name=f".env.{key}",
                data=safe_dump(val, sort_keys=False),
            )
            for key, val in self.env_store.items()
        ]

        result.append(
            LLMResponse(
                type=ResponseType.COMPOSE_FILE,
                name='compose.yml',
                data=safe_dump(parsed_data, sort_keys=False),
            )
        )

        return result

    def assign_param_defaults(self, prompt_params: dict[str, Any]) -> None:
        prompt_params["services"] = (
            prompt_params["services"]
            if isinstance(prompt_params["services"], str)
            else ", ".join(prompt_params["services"])
        )
        prompt_params["project"] = prompt_params["project"] or "demo_project"
        prompt_params["network_name"] = prompt_params["network_name"] or f"{prompt_params['project']}_network"
        prompt_params["network_exists"] = "already exists" if prompt_params["network_exists"] else "should be created"
        prompt_params["volume_mount"] = "docker volumes" if prompt_params["volume_mount"] else "project folder"
        prompt_params["additional_instructions"] = (
            "" if "retry" not in prompt_params else self.TASK_PROMPT_RETRY.format(error=prompt_params["error"])
        )

    def parse_compose_config(self, content: str) -> dict:
        try:
            data: dict = safe_load(content)
        except YAMLError:
            raise ValidationError("safe_load could not load this yaml string")

        if not data.get("networks", None):
            raise ValidationError("missing network configuration")

        if not (services := data.get("services", None)):
            raise ValidationError("missing services configuration")

        services: dict[str, dict]
        for service, values in services.items():
            if not (values.get("image", False)):
                raise ValidationError(f"missing image for service {service}")

            if env := values.get("environment", {}):
                self.env_vars_extract(service, env)
                data["services"][service].pop("environment")
                data["services"][service]["env_file"] = f".env.{service}"

        for volume, params in data.get("volumes", {}).items():
            if params is None:
                data["volumes"][volume] = {}

        return data

    def env_vars_extract(self, service: str, environment: dict[str, Any] | list[str]) -> bool:
        if not environment or not service or service in self.env_store.keys():
            raise ValidationError("empty environment or duplicated service environment")

        if not isinstance(environment, dict) and not isinstance(environment, list):
            raise ValidationError("environment must be dict or list")

        self.env_store[service] = {}
        if isinstance(environment, dict):
            self.env_store[service].update(environment)
            return True

        for item in environment:
            if "=" not in item:
                raise ValidationError(f"invalid list environment element: {item}")

            k, v = item.split("=", 1)
            self.env_store[service][k] = v

        return True
