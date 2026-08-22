from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def normalize_email(value: str) -> str:
    email = value.strip().lower()

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("A valid email address is required.")

    return email


class UserCreateRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    username: str | None = Field(default=None, max_length=80)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class UserResponse(BaseModel):
    id: int
    email: str
    username: str | None
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthLoginResponse(TokenResponse):
    user: UserResponse
