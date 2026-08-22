from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the RepoPulse backend.

    Environment-dependent values are kept here instead of being
    hardcoded throughout routes, services, and integrations.
    """

    app_name: str = "RepoPulse API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # Origin allowed to communicate with the API from the browser.
    # This will later be replaced by the deployed frontend URL.
    frontend_origin: str = "http://localhost:5173"

    # PostgreSQL connection string loaded from .env.
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/repopulse"
    )

    # JWT values are configurable so secrets and token lifetimes are not
    # hardcoded in route or service code.
    jwt_secret_key: str = "change-me-in-local-env-with-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )




@lru_cache
def get_settings() -> Settings:
    """Create application settings once and reuse the same instance."""
    return Settings()
