from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthLoginResponse,
    TokenResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)
from app.services.security import create_access_token
from app.services.users import authenticate_user, create_user, get_user_by_email


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def to_user_response(user: User) -> UserResponse:
    """Convert the SQLAlchemy User model into the public API response shape."""

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a new account and return safe user data.

    Password hashing is handled in the user service. This route only controls
    HTTP behavior such as duplicate-email errors and response status codes.
    """

    if get_user_by_email(db, request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        username=request.username,
    )

    return to_user_response(user)


@router.post(
    "/login",
    response_model=AuthLoginResponse,
)
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
) -> AuthLoginResponse:
    """Authenticate a user and return a JWT plus the current user profile."""

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))

    return AuthLoginResponse(
        access_token=access_token,
        user=to_user_response(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the profile linked to the valid Bearer token."""

    return to_user_response(current_user)


@router.post(
    "/token",
    response_model=TokenResponse,
    include_in_schema=False,
)
def token_alias(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    OAuth2-compatible token endpoint used by FastAPI tooling.

    The main frontend can use /login. This hidden alias keeps FastAPI's
    OAuth2PasswordBearer flow working without exposing duplicate docs.
    """

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(subject=str(user.id)))
