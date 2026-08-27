from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.schemas.user_schema import (
    UserRegister,
    UserResponse,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.models.user_model import User, PasswordResetOTP
from app.database import get_db
from app.auth import (
    hash_password,
    verify_hashed_password,
    create_access_token,
    get_current_user,
)
from app.utils.email_utils import generate_otp, send_otp_email

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


# ---------------------------------------------------------
# Forgot Password & OTP Reset Endpoints
# ---------------------------------------------------------


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    payload: ForgotPasswordRequest, session: AsyncSession = Depends(get_db)
):
    # 1. Check if user with this email exists
    query = select(User).where(User.email == payload.email)
    user = (await session.execute(query)).scalar_one_or_none
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email address",
        )
    # 2. Generate OTP and calculate 10-minute expiry
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # 3. Save OTP in PostgreSQL
    otp_entry = PasswordResetOTP(
        email=payload.email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False,
    )
    session.add(otp_entry)
    await session.commit()

    await send_otp_email(payload.email, otp_code)

    return {"message": "OTP has been sent to your email"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    payload: ResetPasswordRequest, session: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)

    # 1. Find a valid, unexpired, unused OTP matching email and code
    otp_query = (
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.email == payload.email,
            PasswordResetOTP.otp_code == payload.otp,
            PasswordResetOTP.is_used == False,
            PasswordResetOTP.expires_at > now,
        )
        .order_by(PasswordResetOTP.id.desc())
    )

    otp_record = (await session.execute(otp_query)).scalar_one_or_none()

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code",
        )

    user_query = select(User).where(User.email == payload.email)
    user = (await session.execute(user_query)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.password = hash_password(payload.new_password.get_secret_value())
    otp_record.is_used = True

    await session.commit()

    return {"message": "Password reset successfully."}
