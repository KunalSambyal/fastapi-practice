from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator

async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:9628@localhost:5432/kunaltest", echo=True
)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()