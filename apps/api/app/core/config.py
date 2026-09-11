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

    # --- S3-compatible object storage (SeaweedFS in dev; Garage/R2/MinIO in prod) ---
    s3_endpoint: str = "http://localhost:8333"
    s3_access_key: str = "acme"
    s3_secret_key: str = "acme-dev-secret"
    s3_bucket: str = "acme-dev"

    # --- Transactional email over plain SMTP (Mailpit in dev; your MTA/relay in prod) ---
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "acme@localhost"
    smtp_use_tls: bool = False

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
