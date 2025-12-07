# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API metadata
    api_title: str = "Mumbl Backend API"
    api_description: str = "Audio transcription and lyric generation API"
    api_version: str = "1.0.0"

    # CORS / security
    frontend_origin: str = "http://localhost:3000"

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Storage
    upload_dir: str = "uploads"
    min_upload_bytes: int = 1024

    # Whisper / transcription
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute: str = "int8"

    # Genius API (metadata only)
    genius_token: str | None = None  # TODO: set GENIUS_TOKEN in env when ready

    # LLM settings
    llm_provider: str = "cohere"  # e.g., "cohere", "openai"
    llm_api_key: str | None = None  # TODO: set LLM_API_KEY in env when wired
    llm_model: str = "command"  # TODO: adjust per provider

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
