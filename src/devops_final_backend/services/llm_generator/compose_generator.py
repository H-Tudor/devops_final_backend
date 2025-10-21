"""Specialized Generator for Docker Compose"""

from typing import Any

from yaml import YAMLError, safe_dump, safe_load

from .abstract_generator import AbstractGenerator
from .errors import InvalidModelParameters, InvalidModelResponse, ModelFailedToRespond, ValidationError
from .models import LLMResponse, ResponseType


class ComposeGenerator(AbstractGenerator):
    """Specialized Generator for Docker Compose files which inherits constans and methods from the abstract parent"""

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
    Declare all required volumes in the volumes section.
    Map each declared volume to {volume_mount} using named volume references.
    {additional_instructions}
    """
    TASK_PROMPT_PARAMS = ["network_name", "network_exists", "services", "volume_mount"]
    TASK_PROMPT_RETRY = "The previous configuration was invalid because {error}. Regenerate the entire YAML"

    def __init__(self, dry_run: bool = False):
        """Init the abstract generator and create an empty env store"""
        super().__init__()
        self.env_store: dict[str, dict] = {}
        self.dry_run = dry_run

    def run(self, prompt_params: dict[str, Any]) -> list[LLMResponse]:
        """
        Generate a Docker Compose file using a Large Language Model (LLM).

        Args:
            prompt_params (dict[str, Any]): Parameters injected into the LLM prompt.Expected keys:
                - services (list[str]): List of service definitions to include in the compose file.
                Each entry may specify an image in one of the following forms:
                "redis", "mariadb:12", "quay.io/keycloak/keycloak:26.3.2", etc.
                - network_name (str): Name of the Docker network to include in the compose file.
                - network_exists (bool): If True, the network is declared as external;
                otherwise, a new network definition is created.
                - volume_mount (bool): If True, volumes are mounted in Docker's default volume directory;
                otherwise, they are mounted relative to the compose file location.

        Raises:
            InvalidModelParams: If any expected parameters (as defined in TASK_PROMPT_PARAMS) are missing or invalid.
            ModelFailedToRespond: If the LLM fails to produce a response.
            InvalidModelResponse: If the response from the LLM fails validation.

        Returns:
            list[LLMResponse]: A list of responses containing the generated Docker Compose file content.
        """

        result = []
        self.validate_params(prompt_params)
        self.assign_param_defaults(prompt_params)

        if self.dry_run:
            return self.NO_RESPONSE

        try:
            resp = self.get_chain().invoke(prompt_params)
        except Exception as ex:
            raise ModelFailedToRespond() from ex

        if not resp or not resp.text():
            raise ModelFailedToRespond()

        try:
            parsed_data = self.parse_compose_config(resp.text(), prompt_params)
        except ValidationError as err:
            if prompt_params.get("retry", False):
                raise InvalidModelResponse(err.message) from err

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
                name="compose.yml",
                data=safe_dump(parsed_data, sort_keys=False),
            )
        )

        return result

    def assign_param_defaults(self, prompt_params: dict[str, Any]) -> None:
        """Transform the values of the prompt params into LLM prompt injectable stirngs

        Args:
            prompt_params (dict[str, Any]): the values to be changed

        Raises:
            InvalidModelParameters: the services param is empty
        """

        if not prompt_params["services"]:
            raise InvalidModelParameters(["services"])

        prompt_params["services"] = (
            prompt_params["services"]
            if isinstance(prompt_params["services"], str)
            else ", ".join([f"[ {x} ]" for x in prompt_params["services"]])
        )

        prompt_params["network_name"] = prompt_params["network_name"] or "demo_network"
        prompt_params["network_exists"] = (
            prompt_params["network_exists"]
            if isinstance(prompt_params["network_exists"], str)
            else ("already exists" if prompt_params["network_exists"] else "should be created")
        )

        prompt_params["volume_mount"] = (
            prompt_params["volume_mount"]
            if isinstance(prompt_params["volume_mount"], str)
            else ("docker volumes" if prompt_params["volume_mount"] else "project folder")
        )

        prompt_params["additional_instructions"] = (
            "" if "retry" not in prompt_params else self.TASK_PROMPT_RETRY.format(error=prompt_params["error"])
        )

    def parse_compose_config(self, content: str, params: dict) -> dict:
        """Parse the content as a docker compose file yaml and check that required elements
        (services, network) are declared

        Args:
            content (str): the raw string as generated by the LLM
            params (dict): the llm generation parameters

        Raises:
            ValidationError: one of the following criteria is met

                - invalid yaml
                - networks element missing or empty
                - services element missing or empty
                - service image missing or empty
                - service environmnet extraction failed

        Returns:
            dict: the parsed docker compose yaml as dict
        """

        try:
            data: dict = safe_load(content)
        except YAMLError as err:
            raise ValidationError("safe_load could not load this yaml string") from err

        if not data or not isinstance(data, dict):
            raise ValidationError("empty yaml")

        if not (networks := data.get("networks", None)):
            raise ValidationError("missing network configuration")

        if params["network_name"] not in networks:
            raise ValidationError("requested network name not present")

        if (
            params["network_exists"] == "already exists"
            and networks[params["network_name"]].get("external", None) is not True
        ):
            raise ValidationError("requested network name not present")

        if not (services := data.get("services", None)):
            raise ValidationError("missing services configuration")

        for service, values in services.items():
            if not values.get("image", False):
                raise ValidationError(f"missing image for service {service}")

            if env := values.get("environment", {}):
                self.env_vars_extract(service, env)
                data["services"][service].pop("environment")
                data["services"][service]["env_file"] = f".env.{service}"

        if "volumes" in data:
            if not data.get("volumes", {}):
                raise ValidationError("volumes declared but empty")

            for volume, vol_params in data.get("volumes", {}).items():
                if vol_params is None:
                    data["volumes"][volume] = {}

        return data

    def env_vars_extract(self, service: str, environment: dict[str, Any] | list[str]) -> None:
        """Extract the environment variables of the service into a global env_store
        that will be used to generate separate environment files

        Args:
            service (str): the service name that will key the env store
            environment (dict[str, Any] | list[str]): the contents of the environment element

        Raises:
            ValidationError: one of the following criteria is met
                - a service is generated twice
                - invalid environment format (if applicable)
        """

        if not environment or not service or service in self.env_store:
            raise ValidationError("empty environment or duplicated service environment")

        if not isinstance(environment, dict) and not isinstance(environment, list):
            raise ValidationError("environment must be dict or list")

        self.env_store[service] = {}
        if isinstance(environment, dict):
            self.env_store[service].update(environment)
            return

        for item in environment:
            if "=" not in item:
                raise ValidationError(f"invalid list environment element: {item}")

            k, v = item.split("=", 1)
            self.env_store[service][k] = v

        return
