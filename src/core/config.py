import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_ignore_empty=False,
        env_nested_delimiter="_",
        extra="ignore",
    )
    app_name: str = "LlamaBuddy"
    api_str: str = "/api"
    debug: bool = False

    LLAMA_API_KEY: str
    LLAMA_BASE_URL: str
    LLM_MODEL: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    @classmethod
    def validate_env_vars(cls) -> None:
        """
        Validate that all required environment variables are present.
        Exits with error code 1 if any required variables are missing.
        """
        required_vars = [
            "LLAMA_API_KEY",
            "LLAMA_BASE_URL",
            "LLM_MODEL",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
        ]
        missing_vars: List[str] = []

        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)

        if missing_vars:
            error_message = (
                f"Error: Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please set these variables in your environment or .env file."
            )
            print(error_message, file=sys.stderr)
            sys.exit(1)


@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    # Validate required environment variables before creating settings
    Settings.validate_env_vars()
    return Settings()  # noqa


settings = get_settings()
