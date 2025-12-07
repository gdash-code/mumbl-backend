# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    frontend_origin: str = "http://localhost:3000"
    rate_limit_per_minute: int = 60
    upload_dir: str = "uploads"
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute: str = "int8"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
