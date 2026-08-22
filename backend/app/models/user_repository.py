from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.user import User


class UserRepository(Base):
    """
    Per-user tracking relationship for one global Repository row.

    This lets multiple users track the same GitHub repository without
    duplicating repository identity data.
    """

    __tablename__ = "user_repositories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Points at the shared repository record that may be tracked by many users.
    repository_id: Mapped[int] = mapped_column(
        ForeignKey(
            "repositories.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_tracked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    last_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="tracked_repositories",
    )

    repository: Mapped["Repository"] = relationship(
        back_populates="user_repositories",
    )

    __table_args__ = (
        # One user can track a repository only once. Repeated track requests
        # reactivate/reuse this row instead of creating duplicates.
        UniqueConstraint(
            "user_id",
            "repository_id",
            name="uq_user_repositories_user_repository",
        ),
    )
