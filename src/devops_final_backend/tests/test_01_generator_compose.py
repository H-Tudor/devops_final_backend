"""Test 01: LLM Generator

Test that conversions and parsing is working as expected for positive and negative values.
Trigger the codded error cases
"""

# pylint: disable=redefined-outer-name

from typing import Any
from unittest.mock import MagicMock

import pytest
from yaml import safe_dump

from devops_final_backend.services.llm_generator import ComposeGenerator, errors, models


@pytest.fixture
def generator():
    """Get a generator instance that will not call the llm

    Returns:
        ComposeGenerator: the generator instance
    """

    return ComposeGenerator(dry_run=True)


def test_01_assign_param_defaults(generator: ComposeGenerator):
    """Check for a thrown error if no services are declared

    Args:
        generator (ComposeGenerator): generator instance
    """

    params = {
        "services": [],
        "network_name": "",
        "network_exists": False,
        "volume_mount": False,
    }

    with pytest.raises(errors.InvalidModelParameters):
        generator.assign_param_defaults(params)


def test_02_assign_param_first_run_negatives(generator: ComposeGenerator):
    """Check default values for missing or False inputs

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": ["redis", "mariadb:12"],
        "network_name": "",
        "network_exists": False,
        "volume_mount": False,
    }

    generator.assign_param_defaults(params)

    assert params["services"] == "[ redis ], [ mariadb:12 ]"
    assert params["network_name"] == "demo_network"
    assert params["network_exists"] == "should be created"
    assert params["volume_mount"] == "project folder"


def test_03_assign_param_first_run_positives(generator: ComposeGenerator):
    """Check default values overwrite for present or True inputs

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": ["redis", "mariadb:12"],
        "network_name": "test_network",
        "network_exists": True,
        "volume_mount": True,
    }

    generator.assign_param_defaults(params)

    assert params["services"] == "[ redis ], [ mariadb:12 ]"
    assert params["network_name"] == "test_network"
    assert params["network_exists"] == "already exists"
    assert params["volume_mount"] == "docker volumes"


def test_04_assign_param_second_run(generator: ComposeGenerator):
    """Ensure formated values are not overwritten

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": "[ redis ], [ mariadb:12 ]",
        "network_name": "test_network",
        "network_exists": "already exists",
        "volume_mount": "docker volumes",
    }

    generator.assign_param_defaults(params)

    assert params["services"] == "[ redis ], [ mariadb:12 ]"
    assert params["network_name"] == "test_network"
    assert params["network_exists"] == "already exists"
    assert params["volume_mount"] == "docker volumes"


def test_05_parse_compose_config_first_variant(generator: ComposeGenerator):
    """Sanity Check: parsing for when bool params (network_exists, volume_mount) are True

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": "[ redis ]",
        "network_name": "default",
        "network_exists": "should be created",
        "volume_mount": "project folder ",
    }
    yaml_content = """
    version: 3
    services:
      redis:
        image: redis:latest
        environment:
          VAR1: value1
    networks:
      default:
    """

    result = generator.parse_compose_config(yaml_content, params)

    assert "networks" in result
    assert "default" in result["networks"]

    assert "services" in result
    assert "redis" in result["services"]
    assert "image" in result["services"]["redis"]
    assert "env_file" in result["services"]["redis"]
    assert "environment" not in result["services"]["redis"]

    assert "redis" in generator.env_store
    assert "VAR1" in generator.env_store["redis"]


def test_06_parse_compose_config_second_variant(generator: ComposeGenerator):
    """Sanity Check: parsing for when bool params (network_exists, volume_mount) are False

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": "[ redis ]",
        "network_name": "default",
        "network_exists": "already exists",
        "volume_mount": "docker volumes",
    }
    yaml_content = """
    version: 3
    services:
      redis:
        image: redis:latest
        environment:
          VAR1: value1
    networks:
      default:
        external: true
    volumes:
      redis:
    """

    result = generator.parse_compose_config(yaml_content, params)

    assert "volumes" in result
    assert "redis" in result["volumes"]

    assert "networks" in result
    assert "default" in result["networks"]
    assert "external" in result["networks"]["default"]
    assert result["networks"]["default"]["external"] is True

    assert "services" in result
    assert "redis" in result["services"]
    assert "image" in result["services"]["redis"]
    assert "env_file" in result["services"]["redis"]
    assert "environment" not in result["services"]["redis"]


def test_07_parse_compose_config_missing_values(generator: ComposeGenerator):
    """Check if all the required errors are thrown when the compose configuration is invalid

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": "[ redis ]",
        "network_name": "test_network",
        "network_exists": "already exists",
        "volume_mount": "docker volumes",
    }

    with pytest.raises(errors.ValidationError):
        generator.parse_compose_config("invalid", params)

    with pytest.raises(errors.ValidationError):
        generator.parse_compose_config("", params)

    config: dict[str, Any] = {"version": 3, "services": {"redis": {"image": "redis"}}}
    with pytest.raises(errors.ValidationError):
        # missing network
        generator.parse_compose_config(safe_dump(config), params)

    config["networks"] = {}
    with pytest.raises(errors.ValidationError):
        # empty networ
        generator.parse_compose_config(safe_dump(config), params)

    config["networks"]["demo_network"] = {}
    with pytest.raises(errors.ValidationError):
        # requested network not in generated networks
        generator.parse_compose_config(safe_dump(config), params)

    del config["networks"]["demo_network"]
    config["networks"]["test_network"] = {}
    with pytest.raises(errors.ValidationError):
        # requested external network exists but does not external atribute
        generator.parse_compose_config(safe_dump(config), params)

    config["networks"]["test_network"]["external"] = False
    with pytest.raises(errors.ValidationError):
        # requested external network exists but it is not marked as external
        generator.parse_compose_config(safe_dump(config), params)

    config["networks"]["test_network"]["external"] = True
    config["volumes"] = {}
    with pytest.raises(errors.ValidationError):
        # fails for empty volumes element
        generator.parse_compose_config(safe_dump(config), params)

    config["services"] = {}
    del config["volumes"]
    with pytest.raises(errors.ValidationError):
        # fails for missing services
        generator.parse_compose_config(safe_dump(config), params)

    config["services"] = {"redis": {}}
    with pytest.raises(errors.ValidationError):
        # fails for missing service image
        generator.parse_compose_config(safe_dump(config), params)


def test_08_env_vars_extract_dict(generator: ComposeGenerator):
    """Sanity Check: ensure correct dict env parsing

    Args:
        generator (ComposeGenerator): instance
    """

    env = {"KEY": "VALUE"}
    generator.env_vars_extract("service1", env)
    assert generator.env_store["service1"] == env


def test_09_env_vars_extract_list(generator: ComposeGenerator):
    """Sanity Check: ensure correct list env parsing

    Args:
        generator (ComposeGenerator): instance
    """

    env = ["FOO=bar", "BAZ=qux"]
    generator.env_vars_extract("service2", env)
    assert generator.env_store["service2"] == {"FOO": "bar", "BAZ": "qux"}


def test_10_env_vars_extract_missing_prerequisites(generator: ComposeGenerator):
    """Check that ValidationErrors are being thrown for invalid environment

    Args:
        generator (ComposeGenerator): instance
    """

    service_name = "test"
    env = {"test": "test"}

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("test", {})

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("test", [])

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("", env)

    generator.env_store[service_name] = env
    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract(service_name, env)


def test_11_run_dry_run_returns_dummy(generator: ComposeGenerator):
    """Check that dry-run response works

    Args:
        generator (ComposeGenerator): instance
    """

    params = {
        "services": ["redis"],
        "network_name": "net",
        "network_exists": False,
        "volume_mount": False,
    }

    result = generator.run(params)

    assert result[0].type == models.ResponseType.NO_RESPONSE
    assert result[0].data == "Lorem Ipsum"


def test_12_run_invalid_response_triggers_retry(monkeypatch):
    """Check that on retry failure ends with an invalid model response error.

    This works by patching the chain.invoke method that is present in the generator object
    with a fake invoke that returns an invalid yaml. The fake structure must be declared inside
    the test function body so that it can set the tested value of call_count

    Args:
        monkeypatch (Any): instance
    """

    gen = ComposeGenerator(dry_run=False)
    call_count = {"count": 0}

    def fake_invoke(_params):
        call_count["count"] += 1

        # pylint: disable=too-few-public-methods
        class Resp:
            """Fake response for invalid YAML."""

            def text(self):
                """Return invalid YAML text."""
                return "invalid_yaml:"

        return Resp()

    monkeypatch.setattr(gen, "get_chain", lambda: MagicMock(invoke=fake_invoke))
    params = {
        "services": ["redis"],
        "network_name": "net",
        "network_exists": False,
        "volume_mount": False,
    }

    with pytest.raises(errors.InvalidModelResponse):
        gen.run(params)

    assert call_count["count"] == 2
