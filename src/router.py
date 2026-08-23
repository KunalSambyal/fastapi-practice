from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.exc import IntegrityError

from .db import get_db
from .models import Users
from .schemas import UserRegister, UserResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/users", response_model=list[UserResponse])
async def get_users(session: AsyncSession = Depends(get_db)):
    query = select(Users)
    res = await session.execute(query)
    return res.scalars().all()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user_data: UserRegister, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(Users).where(Users.username == user_data.username)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists."
        )

    result = await session.execute(select(Users).where(Users.email == user_data.email))

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists."
        )

    user = Users(
        username=user_data.username, email=user_data.email, password=user_data.password
    )
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists.",
        )

    return user
