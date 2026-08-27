from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
import re


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        max_length=100,
        min_length=3,
        pattern=r"^\w+$",
        description="Unique username containig alpha, numeric and underscore characters.",
        examples=["john_12", "john532"],
    )
    email: EmailStr = Field(..., description="Unique Email")
    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Password containing one uppercase, one lowercase, one digit and a special character between 8-20.",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        password = v.get_secret_value()

        # Use Python's re module for full regex support (look-aheads work here)
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain a special character")

        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str = Field(..., description="Username of the user")
    password: SecretStr = Field(..., description="Password of the user")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email of the user")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email of the user")
    otp: str = Field(
        ...,
        min_length=4,
        max_length=6,
        pattern=r"^\d+$",
        description="Numeric OTP received on email",
        examples=["437323"],
    )
    new_password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=20,
        description="New password containing uppercase, lowercase, digit, and special char.",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: SecretStr) -> SecretStr:
        password = v.get_secret_value()

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain a special character")

        return v
