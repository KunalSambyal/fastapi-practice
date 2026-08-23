from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DB_URL")

async_engine = create_async_engine(DB_URL)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
