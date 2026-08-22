from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Repository(Base):
    """
    GitHub repository tracked by RepoPulse.

    Analysis results will be stored separately so repository
    information and historical analysis data remain independent.
    """

    __tablename__ = "repositories"

    # Internal RepoPulse database identifier.
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    # GitHub repository identity.
    github_owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    github_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    repository_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
    )

    # Determines whether scheduled analysis should continue.
    is_tracked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # When RepoPulse last analyzed this repository.
    last_analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Record creation time.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )