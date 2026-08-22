from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisSnapshot(Base):
    """
    Historical RepoPulse analysis captured for one repository.

    A new snapshot can be stored whenever a tracked repository
    is re-analyzed.
    """

    __tablename__ = "analysis_snapshots"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    # Repository this analysis belongs to.
    repository_id: Mapped[int] = mapped_column(
        ForeignKey(
            "repositories.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Activity metrics.
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

    # We'll eventually replace/expand this with the
    # complete RepoPulse scoring engine.
    health_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    repository: Mapped["Repository"] = relationship(
        back_populates="analysis_snapshots",
    )