from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date


class Address(BaseModel):
    city: str = Field(..., title="City", max_length=100)
    state: str = Field(..., title="State", max_length=100)
    country: Optional[str] = Field("INDIA", title="Country", max_length=100)
    zip: Optional[str] = Field(None, title="Zip", max_length=10)


class CredentialOut(BaseModel):
    username: str = Field(..., title="Username", min_length=3, max_length=100)
    email: EmailStr = Field(..., title="Email Address")


class CredentialIn(CredentialOut):
    password: str = Field(
        ..., title="Password", min_length=8, max_length=32, exclude=True
    )


class StudentIn(BaseModel):
    std_id: int = Field(..., title="Student ID", gt=1000)
    std_name: str = Field(
        ..., title="Student Name", max_length=100, min_length=3, examples=["Jon Snow"]
    )
    std_age: int = Field(..., title="Student Age", gt=4, le=20)
    std_dob: date = Field(..., examples=["2021-11-29"])
    std_address: Address = Field(..., title="Student Address")
    std_credentials: CredentialIn = Field(..., title="Student Credentials")


class StudentOut(StudentIn):
    std_credentials: CredentialOut = Field(..., title="Student Credentials")
