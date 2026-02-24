import logging
import secrets

from pydantic import model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


def _ensure_async_url(url: str) -> str:
    """Convert standard postgres:// URLs to use the asyncpg driver.

    Also strips ``sslmode`` from the query string because asyncpg does not
    accept it — SSL is instead configured via ``connect_args`` in database.py.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # asyncpg doesn't understand the libpq `sslmode` param — strip it
    if "sslmode" in url:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params.pop("sslmode", None)
        new_query = urlencode(params, doseq=True)
        url = urlunparse(parsed._replace(query=new_query))

    return url


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/career_planner.db"
    gemini_api_key: str = ""
    groq_api_key: str = ""
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.hf.space",
    ]
    secret_key: str = ""
    access_token_expire_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def _fixup(self) -> "Settings":
        # Ensure PostgreSQL URLs use the asyncpg driver
        self.database_url = _ensure_async_url(self.database_url)
        # Generate a random secret key if none provided
        if not self.secret_key:
            if hasattr(self, "model_fields"):  # pydantic v2
                import os
                if os.environ.get("SPACE_ID"):
                    logger.warning(
                        "SECRET_KEY not set in production! "
                        "Set the SECRET_KEY environment variable."
                    )
            self.secret_key = secrets.token_urlsafe(32)
        return self


settings = Settings()
