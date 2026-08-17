from typing import Any, TypeVar
from sqlalchemy import delete, select
from sqlalchemy.sql import Executable
from .connection import AsyncSessionFactory
from .base import Base

T = TypeVar("T", bound=Base)


async def fetch_one(query: Executable) -> Any | None:
    """Execute a query and return a single scalar model instance or None."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(query)
        return result.scalars().first()


async def fetch_all(query: Executable) -> list[Any]:
    """Execute a query and return all scalar model instances as a list."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(query)
        return list(result.scalars().all())


async def create(instance: T) -> int:
    """Persist a new model instance and return its generated primary key ID."""
    async with AsyncSessionFactory() as session:
        async with session.begin():
            session.add(instance)
            await session.flush()
            return getattr(instance, "id")


async def update(instance: T) -> int:
    """Merge modifications on an existing model instance and commit."""
    async with AsyncSessionFactory() as session:
        async with session.begin():
            merged = await session.merge(instance)
            await session.flush()
            return getattr(merged, "id")


async def delete_by_id(model_class: type[T], record_id: int) -> None:
    """Delete a record by its primary key ID."""
    async with AsyncSessionFactory() as session:
        async with session.begin():
            stmt = delete(model_class).where(getattr(model_class, "id") == record_id)
            await session.execute(stmt)
