from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LLM_PROVIDER: Literal["anthropic", "openai"] = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    OPENAI_MODEL: str = "gpt-4o"
    MAX_SUPERVISOR_ITERATIONS: int = 5
    LOG_LEVEL: str = "INFO"
    QDRANT_URL: str = ":memory:"  # in-memory for demo; use "http://localhost:6333" for production

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
