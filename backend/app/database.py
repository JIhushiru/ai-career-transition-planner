from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base

connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_async_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Lightweight migration: add columns that may be missing on existing DBs
        await _add_column_if_missing(conn, "users", "years_experience", "INTEGER")


async def _add_column_if_missing(conn, table: str, column: str, col_type: str):
    """SQLite-compatible: add a column if it doesn't already exist."""
    from sqlalchemy import text

    result = await conn.execute(text(f"PRAGMA table_info({table})"))
    columns = [row[1] for row in result]
    if column not in columns:
        await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
