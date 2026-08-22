from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def normalize_email(value: str) -> str:
    """Normalize email input and reject obviously invalid addresses."""

    email = value.strip().lower()

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("A valid email address is required.")

    return email


class UserCreateRequest(BaseModel):
    """Request body for creating a new user account."""

    email: str
    password: str = Field(min_length=8, max_length=128)
    username: str | None = Field(default=None, max_length=80)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class UserLoginRequest(BaseModel):
    """Request body for password-based login."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class UserResponse(BaseModel):
    """Safe user data returned to clients."""

    id: int
    email: str
    username: str | None
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Bearer token response shape used by auth endpoints."""

    access_token: str
    token_type: str = "bearer"


class AuthLoginResponse(TokenResponse):
    """Login response that includes both token data and user profile data."""

    user: UserResponse
