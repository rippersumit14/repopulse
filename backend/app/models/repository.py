from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.analysis_snapshot import AnalysisSnapshot
    from app.models.user_repository import UserRepository


class Repository(Base):
    """
    GitHub repository tracked by RepoPulse.

    Repository identity is stored here while historical analysis
    results are stored separately in analysis_snapshots.
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

    # Whether background analysis should continue for this repository.
    is_tracked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Most recent successful repository analysis.
    last_analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # When the repository was first added to RepoPulse.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # One repository can have many historical analysis snapshots.
    analysis_snapshots: Mapped[list["AnalysisSnapshot"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user_repositories: Mapped[list["UserRepository"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
