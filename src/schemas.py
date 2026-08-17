from pydantic import BaseModel, Field, EmailStr, field_validator


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        examples=["kunal2321"],
        description="Username containing letters, numbers, and underscores.",
        min_length=2,
        max_length=30,
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=32)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if not value.replace("_", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("Password cannot start or end with whitespace")

        if value.isalpha():
            raise ValueError("Password cannot contain only letters")

        if value.isdigit():
            raise ValueError("Password cannot contain only numbers")

        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter")

        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number")

        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
