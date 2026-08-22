from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.repository import Repository


class AnalysisSnapshot(Base):
    """
    Historical analysis captured for a tracked repository.

    Each new analysis creates a new row instead of overwriting
    the previous one. This gives RepoPulse historical trend data.
    """

    __tablename__ = "analysis_snapshots"

    # Internal snapshot identifier.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # Repository this snapshot belongs to.
    repository_id: Mapped[int] = mapped_column(
        ForeignKey(
            "repositories.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # Repository popularity / maintenance metrics.
    stars: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    forks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    open_issues: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    contributors_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Commit activity metrics.
    commits_last_7_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    commits_last_30_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    activity_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Overall RepoPulse score.
    # This will be populated by the health-score engine later.
    health_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Time when this snapshot was created.
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Many snapshots belong to one repository.
    repository: Mapped["Repository"] = relationship(
        back_populates="analysis_snapshots",
    )

    # Optimizes history queries such as:
    # repository_id = X ordered/filter by analyzed_at.
    __table_args__ = (
        Index(
            "ix_analysis_snapshots_repository_analyzed_at",
            "repository_id",
            "analyzed_at",
        ),
    )