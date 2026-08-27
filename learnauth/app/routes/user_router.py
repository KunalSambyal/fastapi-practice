from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.user_schema import (
    UserRegister,
    UserResponse,
    Token,
)
from app.models.user_model import User
from app.database import get_db
from app.auth import (
    hash_password,
    verify_hashed_password,
    create_access_token,
    get_current_user,
)

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
        password=hash_password(user_data.password.get_secret_value()),
    )

    # Add the new user to the session and commit
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.username == form_data.username)
    result = (await session.execute(query)).scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the password
    if not verify_hashed_password(form_data.password, result.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": result.username})

    return {"access_token": token, "token_type": "bearer"}


# Protected route
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user
