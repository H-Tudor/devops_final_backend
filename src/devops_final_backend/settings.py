from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application Settings as retrieved fron environment (.env file if exists or shell)"""

    class Config:
        """Settings retrieval parameters"""
        env_file = Path(".env") if Path(".env").exists() else None
        env_file_encoding = "utf-8"

    app_name: str
    app_version: str
    debug: bool = False

    # LLM
    llm_model: str
    llm_provider: str
    llm_secret: str | None = None

    # Keycloak
    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str


settings = Settings()
