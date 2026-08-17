from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"
    cors_origins: str = "*"

    # Directory the Blue Book PDF is stored in. In production this MUST be a
    # Railway Volume mount path (e.g. /data/blue-book) — without one, this is
    # just the container's ephemeral disk and the file is lost on next deploy.
    blue_book_storage_dir: str = "./blue_book_storage"
    blue_book_max_size_mb: int = 150


@lru_cache
def get_settings() -> Settings:
    return Settings()
