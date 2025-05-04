import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_ignore_empty=False,
        extra="ignore",
    )
    app_name: str = "LlamaBuddy"
    api_str: str = "/api"
    debug: bool = False
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
