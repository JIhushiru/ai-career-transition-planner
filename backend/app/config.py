import logging
import os
import secrets

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


def _default_database_url() -> str:
    """Use DATABASE_URL env var if set (Neon/PostgreSQL), else local SQLite."""
    env_url = os.environ.get("DATABASE_URL", "")
    if env_url:
        # Support Neon/Supabase URLs: postgres:// → postgresql+asyncpg://
        if env_url.startswith("postgres://"):
            return env_url.replace("postgres://", "postgresql+asyncpg://", 1)
        if env_url.startswith("postgresql://"):
            return env_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return env_url
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
