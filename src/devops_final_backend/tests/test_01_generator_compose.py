""" Test 01: LLM Generator

Test that conversions and parsing is working as expected for positive and negative values.
Trigger the codded error cases
"""

from unittest.mock import MagicMock

import pytest
from yaml import safe_dump

from devops_final_backend.services.llm_generator import errors, models
from devops_final_backend.services.llm_generator.compose_generator import ComposeGenerator


@pytest.fixture
def generator():
    return ComposeGenerator(dry_run=True)


# assign
def test_assign_param_defaults(generator: ComposeGenerator):
    params = {
        "services": [],
        "network_name": "",
        "network_exists": False,
        "volume_mount": False,
    }

    with pytest.raises(errors.InvalidModelParameters):
        generator.assign_param_defaults(params)


def test_assign_param_first_run_negatives(generator: ComposeGenerator):
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


def test_assign_param_first_run_positives(generator: ComposeGenerator):
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


def test_assign_param_second_run(generator: ComposeGenerator):
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


def test_parse_compose_config_first_variant(generator: ComposeGenerator):
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


def test_parse_compose_config_second_variant(generator: ComposeGenerator):
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

    result = generator.parse_compose_config(yaml_content, params )

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


def test_parse_compose_config_missing_values(generator: ComposeGenerator):
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

    config = {"version": 3, "services": {"redis": {"image": "redis"}}}
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

def test_env_vars_extract_dict(generator: ComposeGenerator):
    env = {"KEY": "VALUE"}
    generator.env_vars_extract("service1", env)
    assert generator.env_store["service1"] == env


def test_env_vars_extract_list(generator: ComposeGenerator):
    env = ["FOO=bar", "BAZ=qux"]
    generator.env_vars_extract("service2", env)
    assert generator.env_store["service2"] == {"FOO": "bar", "BAZ": "qux"}


def test_env_vars_extract_missing_prerequisites(generator: ComposeGenerator):
    service_name = "test"
    env = {"test": "test"}

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("test", {})

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("test", [])

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("test", "")

    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract("", env)

    generator.env_store[service_name] = env
    with pytest.raises(errors.ValidationError):
        generator.env_vars_extract(service_name, env)


def test_run_dry_run_returns_dummy(generator: ComposeGenerator):
    params = {
        "services": ["redis"],
        "network_name": "net",
        "network_exists": False,
        "volume_mount": False,
    }

    result = generator.run(params)

    assert result[0].type == models.ResponseType.NO_RESPONSE
    assert result[0].data == "Lorem Ipsum"


def test_run_invalid_response_triggers_retry(monkeypatch):
    gen = ComposeGenerator(dry_run=False)
    call_count = {"count": 0}

    def fake_invoke(params):
        call_count["count"] += 1

        class Resp:
            def text(self_inner):
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
