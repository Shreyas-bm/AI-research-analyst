import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.app.config import settings

Base = declarative_base()

# Determine database url, fallback gracefully
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    # Ensure SQLite directory exists
    sqlite_path = db_url.replace("sqlite+aiosqlite:///", "")
    if sqlite_path and os.path.dirname(sqlite_path):
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        pool_pre_ping=True
    )

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
