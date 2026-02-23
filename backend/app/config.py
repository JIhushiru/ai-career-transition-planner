import logging
import os
import secrets
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


def _default_database_url() -> str:
    """Use HF Spaces persistent /data dir if available, else local ./data."""
    if os.environ.get("SPACE_ID"):
        # Running on HF Spaces — use /data for persistence across rebuilds
        Path("/data").mkdir(parents=True, exist_ok=True)
        return "sqlite+aiosqlite:////data/career_planner.db"
    return "sqlite+aiosqlite:///./data/career_planner.db"


def _default_secret_key() -> str:
    """Generate a random secret key if none is provided. Warn in production."""
    if os.environ.get("SPACE_ID"):
        logger.warning(
            "SECRET_KEY not set in production! Set the SECRET_KEY environment variable."
        )
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    database_url: str = _default_database_url()
    gemini_api_key: str = ""
    groq_api_key: str = ""
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.hf.space",
    ]
    secret_key: str = _default_secret_key()
    access_token_expire_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
