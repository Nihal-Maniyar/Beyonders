"""Configuration settings for LearnLoop AI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings:
    def __init__(self):
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
        self.database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/learnloop.db")
        self.data_dir: Path = DATA_DIR

        # Optional LLM integration
        self.llm_provider: Optional[str] = os.getenv("LLM_PROVIDER")
        self.llm_api_key: Optional[str] = os.getenv("LLM_API_KEY")
        self.llm_model: Optional[str] = os.getenv("LLM_MODEL")

        # Optional Voice integration
        self.elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    @property
    def has_llm(self) -> bool:
        return bool(self.llm_api_key and self.llm_provider)

    @property
    def has_tts(self) -> bool:
        return bool(self.elevenlabs_api_key)


settings = Settings()
