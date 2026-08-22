from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.security import hash_password, verify_password


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Return one user by primary key, or None when the id is unknown."""

    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Look up users by normalized email address."""

    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    username: str | None = None,
) -> User:
    """Create a user with a hashed password inside one database transaction."""

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
    )

    try:
        # Commit here so route code receives database-generated fields such as
        # id and created_at immediately after registration.
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user


def authenticate_user(
    db: Session,
    *,
    email: str,
    password: str,
) -> User | None:
    """Return the user when email and password are valid, otherwise None."""

    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
