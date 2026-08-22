import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.services.security import decode_access_token
from app.services.users import get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the logged-in user from the Bearer token.

    Protected routes depend on this function. If the token is missing,
    expired, malformed, or points to an inactive user, FastAPI returns 401.
    """

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # JWT validation happens in the security service so every protected
        # route follows the same token rules.
        payload = decode_access_token(token)
        subject = payload.get("sub")
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    if subject is None:
        raise credentials_error

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise credentials_error from exc

    # The token stores only the user id. The database remains the source of
    # truth for current user state such as is_active.
    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None or not user.is_active:
        raise credentials_error

    return user
