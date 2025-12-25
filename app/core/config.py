# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama2"
    LLM_BASE_URL: str = "http://localhost:11434/api"

    OPENAI_API_KEY: str | None = None
    NVIDIA_API_KEY: str | None = None

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
