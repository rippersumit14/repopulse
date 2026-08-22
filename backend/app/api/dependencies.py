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
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
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

    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None or not user.is_active:
        raise credentials_error

    return user
