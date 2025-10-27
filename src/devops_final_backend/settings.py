"""Application Environment Settings"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application Settings as retrieved fron environment (.env file if exists or shell)"""

    model_config = {"env_file": Path(".env") if Path(".env").exists() else None, "env_file_encoding": "utf-8"}

    app_name: str
    app_version: str
    debug: bool = False
    disable_api_testing: bool = False

    # LLM
    llm_model: str
    llm_provider: str
    llm_dry_run: bool = False
    llm_secret: str | None = None
    llm_base_url: str | None = None

    # Keycloak
    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str
    keycloak_test_username: str | None = None
    keycloak_test_password: str | None = None


settings = Settings.model_validate({})
