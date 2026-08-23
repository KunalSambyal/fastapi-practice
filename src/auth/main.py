from fastapi import FastAPI, Header, HTTPException, status, Depends
from jose import jwt
from datetime import datetime, timedelta, timezone

from .models import Users
from .schemas import UserLogin, TokenResponse
from .dao import get_user_by_username, get_user_by_id

app = FastAPI()

JWT_KEY = "super_seceret_jwt_key"
JWT_ALGO = "HS256"


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, JWT_KEY, algorithm=JWT_ALGO)

    return token


# Token generate
@app.post("/auth/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_user(user_data):
    existing_user = await get_user_by_username(user_data.username)
    if not existing_user or existing_user.password != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token(
        {
            "sub": existing_user.username,
            "email": existing_user.email,
            "id": existing_user.id,
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}
