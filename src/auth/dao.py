from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from .db import get_db
from .models import Users


async def get_user_by_username(
    username: str, session: AsyncSession = Depends(get_db)
) -> Users | None:
    result = await session.execute(select(Users).where(Users.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_db)
) -> Users | None:
    result = await session.execute(select(Users).where(Users.id == user_id))
    return result.scalar_one_or_none()
