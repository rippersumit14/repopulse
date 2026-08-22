from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.models.user import User
from app.models.user_repository import UserRepository


def get_repository_by_url(
    db: Session,
    repository_url: str,
) -> Repository | None:
    """
    Find a repository using its normalized GitHub URL.

    Returns None when the repository has never been stored.
    """

    statement = select(Repository).where(
        Repository.repository_url == repository_url
    )

    return db.scalar(statement)


def create_repository(
    db: Session,
    *,
    github_owner: str,
    github_name: str,
    repository_url: str,
) -> Repository:
    """
    Store a new GitHub repository in PostgreSQL
    and enable scheduled tracking for it.
    """

    repository = Repository(
        github_owner=github_owner,
        github_name=github_name,
        repository_url=repository_url,
        is_tracked=True,
    )

    try:
        # Tell SQLAlchemy that this object should be inserted.
        db.add(repository)

        # Permanently save the current transaction.
        db.commit()

        # Reload database-generated values such as id and created_at.
        db.refresh(repository)

    except Exception:
        # A failed transaction must be rolled back before
        # the session can safely be used again.
        db.rollback()
        raise

    return repository


def track_repository(
    db: Session,
    *,
    github_owner: str,
    github_name: str,
    repository_url: str,
) -> tuple[Repository, bool]:
    """
    Track a GitHub repository.

    Returns:
        (repository, created)

    created=True:
        A new database row was created.

    created=False:
        The repository already existed.
    """

    existing_repository = get_repository_by_url(
        db=db,
        repository_url=repository_url,
    )

    # Avoid storing the same GitHub repository more than once.
    if existing_repository is not None:

        # If the repository was previously untracked,
        # enable tracking again instead of creating a duplicate row.
        if not existing_repository.is_tracked:
            existing_repository.is_tracked = True

            try:
                db.commit()
                db.refresh(existing_repository)

            except Exception:
                db.rollback()
                raise

        return existing_repository, False

    repository = create_repository(
        db=db,
        github_owner=github_owner,
        github_name=github_name,
        repository_url=repository_url,
    )

    return repository, True


def get_user_repository(
    db: Session,
    *,
    user_id: int,
    repository_id: int,
) -> UserRepository | None:
    statement = select(UserRepository).where(
        UserRepository.user_id == user_id,
        UserRepository.repository_id == repository_id,
    )

    return db.scalar(statement)


def user_tracks_repository(
    db: Session,
    *,
    user_id: int,
    repository_id: int,
) -> bool:
    tracked_repository = get_user_repository(
        db=db,
        user_id=user_id,
        repository_id=repository_id,
    )

    return tracked_repository is not None and tracked_repository.is_tracked


def track_repository_for_user(
    db: Session,
    *,
    user: User,
    github_owner: str,
    github_name: str,
    repository_url: str,
) -> tuple[Repository, UserRepository, bool]:
    """
    Track a repository for one authenticated user.

    The Repository row is global. UserRepository stores ownership/tracking.
    """

    repository, _ = track_repository(
        db=db,
        github_owner=github_owner,
        github_name=github_name,
        repository_url=repository_url,
    )

    existing_user_repository = get_user_repository(
        db=db,
        user_id=user.id,
        repository_id=repository.id,
    )

    if existing_user_repository is not None:
        if not existing_user_repository.is_tracked:
            existing_user_repository.is_tracked = True

            try:
                db.commit()
                db.refresh(existing_user_repository)
            except Exception:
                db.rollback()
                raise

        return repository, existing_user_repository, False

    user_repository = UserRepository(
        user_id=user.id,
        repository_id=repository.id,
        is_tracked=True,
    )

    try:
        db.add(user_repository)
        db.commit()
        db.refresh(user_repository)
    except Exception:
        db.rollback()
        raise

    return repository, user_repository, True
