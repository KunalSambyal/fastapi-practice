from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.user_schema import (
    UserRegister,
    UserResponse,
    UserLogin,
    UserLoginResponse,
)
from app.models.user_model import User
from app.database import get_db

from app.auth import create_token, verify_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user_data: UserRegister, session: AsyncSession = Depends(get_db)):

    # Check if username or email already exists in the database
    existing = select(User).where(User.username == user_data.username)
    result = (await session.execute(existing)).scalar_one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    existing = select(User).where(User.email == user_data.email)
    result = (await session.execute(existing)).scalar_one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    # Create a new user instance
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password.get_secret_value(),
    )

    # Add the new user to the session and commit
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login_user(user_data: UserLogin, session: AsyncSession = Depends(get_db)):

    existing = select(User).where(User.username == user_data.username)
    result = (await session.execute(existing)).scalar_one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify the password
    if result.password != user_data.password.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    token = create_token({"sub": str(result.id)})

    return {"access_token": token}


# protected route
@router.get("/me")
async def get_user(user=Depends(verify_token)):
    return {"msg": "secure route", "user": user}
