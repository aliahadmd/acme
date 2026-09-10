"""Runtime configuration — every field maps to an entry in `.env.example`.

Full environment matrix (local / CI / prod): docs/environments.md.
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "acme-api"
    environment: Literal["local", "production"] = "local"
    log_level: str = "INFO"
    database_url: str
    # NoDecode: env value arrives as a raw string, split on commas below
    # (instead of pydantic-settings' default JSON decoding).
    cors_origins: Annotated[list[str], NoDecode] = []
    redis_url: str | None = None  # reserved for future use (caching, queues)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Instantiate once; fails fast at startup if required vars are missing."""
    return Settings()
