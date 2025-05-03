from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

print("Loading settings from .env file...")
# Get the root directory of the project
root_dir = Path(__file__).resolve().parent.parent.parent
print(f"Root directory: {root_dir}")


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
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
