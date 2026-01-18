# app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ============================================
    # LLM Provider
    # ============================================
    LLM_PROVIDER: str = "ollama"

    # ============================================
    # Ollama / llama.cpp
    # ============================================
    LLM_MODEL: str = "llama2"
    LLM_BASE_URL: str = "http://localhost:11434/api"

    # ============================================
    # Hugging Face (optional)
    # ============================================
    HF_API_TOKEN: str | None = None
    HF_MODEL_NAME: str | None = None

    # ============================================
    # Groq
    # ============================================
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # ============================================
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
