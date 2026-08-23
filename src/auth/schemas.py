from pydantic import BaseModel, Field, EmailStr, field_validator


class UserLogin(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex=r"^[a-zA-Z0-9_.-]+$",
        description="Username must be alphanumeric and can include underscores, hyphens, and periods.",
        example=["john_doe", "jane-doe", "user.name"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Password must be between 8 and 20 characters long and include at least one digit, one uppercase letter, and one lowercase letter.",
        example=["PasswOrd123"],
    )

    @field_validator("password")
    def validate_password(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
