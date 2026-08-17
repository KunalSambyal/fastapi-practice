from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DB_URL = "postgresql+asyncpg://postgres:9628@localhost:5432/kunaltest"
async_engine = create_async_engine(DB_URL, echo=False)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
