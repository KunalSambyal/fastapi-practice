from collections.abc import AsyncGenerator
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()
DB_URL = os.getenv("DB_URL")

async_engine = create_async_engine(
    DB_URL,
    echo=False,  # Set to True for SQL query debugging
    pool_size=20,  # Connection pool size
    max_overflow=10,  # Additional burst connections
    pool_recycle=1800,  # Recycle connections after 30 minutes
)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # MANDATORY in Async mode to access object attributes post-commit
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session per request"""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
