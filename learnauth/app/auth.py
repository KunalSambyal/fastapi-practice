from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

# from app.routes.user_router import router as auth_router

from dotenv import load_dotenv
import os

load_dotenv()
JWT_KEY = os.getenv("JWT_KEY")
JWT_ALGO = os.getenv("JWT_ALGO")
ACCESS_TOKEN_EXIPRY_MIN = 30


password_hash = PasswordHash.recommended()
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


# password hasing
# pwd_context = CryptContext(schemes=["bycrypt"])

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_hashed_password(plain_pass, hashed_pass):
#     return pwd_context.verify(plain_pass, hashed_pass)


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# def create_token(data: dict):
#     to_encode = data.copy()
#     expiry_time = datetime.now(timezone.utc) + timedelta(minutes=30)

#     to_encode.update({"exp": expiry_time})

#     token = jwt.encode(to_encode, JWT_KEY, algorithm=JWT_ALGO)

#     return token


# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGO])
#         return payload
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token"
#         )
