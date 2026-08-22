from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis_snapshot import AnalysisSnapshot
from app.schemas.repository import HistoryRange, RepositoryHistoryPoint


def create_snapshot(
    db: Session,
    *,
    repository_id: int,
    stars: int,
    forks: int,
    open_issues: int,
    contributors_count: int,
    commits_last_7_days: int,
    commits_last_30_days: int,
    activity_level: str,
    health_score: float,
) -> AnalysisSnapshot:
    """Persist one analysis result as a historical snapshot."""

    snapshot = AnalysisSnapshot(
        repository_id=repository_id,
        stars=stars,
        forks=forks,
        open_issues=open_issues,
        contributors_count=contributors_count,
        commits_last_7_days=commits_last_7_days,
        commits_last_30_days=commits_last_30_days,
        activity_level=activity_level,
        health_score=health_score,
    )

    try:
        # Refresh after commit so callers can read id/analyzed_at immediately.
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
    except Exception:
        db.rollback()
        raise

    return snapshot


def get_latest_snapshot(
    db: Session,
    *,
    repository_id: int,
) -> AnalysisSnapshot | None:
    """Return the newest snapshot for a repository."""

    statement = (
        select(AnalysisSnapshot)
        .where(AnalysisSnapshot.repository_id == repository_id)
        .order_by(AnalysisSnapshot.analyzed_at.desc())
        .limit(1)
    )

    return db.scalar(statement)


def get_repository_snapshots(
    db: Session,
    *,
    repository_id: int,
    history_range: HistoryRange,
) -> list[AnalysisSnapshot]:
    """Load snapshots for the requested chart range in chronological order."""

    now = datetime.now(timezone.utc)

    if history_range == "7d":
        start = now - timedelta(days=7)
    elif history_range == "30d":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=365)

    statement = (
        select(AnalysisSnapshot)
        .where(
            AnalysisSnapshot.repository_id == repository_id,
            AnalysisSnapshot.analyzed_at >= start,
        )
        .order_by(AnalysisSnapshot.analyzed_at.asc())
    )

    return list(db.scalars(statement))


def build_history_points(
    snapshots: list[AnalysisSnapshot],
    *,
    history_range: HistoryRange,
) -> list[RepositoryHistoryPoint]:
    """Convert database snapshots into lightweight chart points."""

    if history_range != "12m":
        return [
            RepositoryHistoryPoint(
                date=snapshot.analyzed_at.date(),
                health_score=snapshot.health_score,
                commits_last_30_days=snapshot.commits_last_30_days,
                stars=snapshot.stars,
                open_issues=snapshot.open_issues,
            )
            for snapshot in snapshots
        ]

    latest_by_month: dict[date, AnalysisSnapshot] = {}

    # For yearly charts, keep one point per month so the frontend receives a
    # compact trend instead of many daily rows.
    for snapshot in snapshots:
        month = date(
            snapshot.analyzed_at.year,
            snapshot.analyzed_at.month,
            1,
        )
        latest_by_month[month] = snapshot

    return [
        RepositoryHistoryPoint(
            date=month,
            health_score=snapshot.health_score,
            commits_last_30_days=snapshot.commits_last_30_days,
            stars=snapshot.stars,
            open_issues=snapshot.open_issues,
        )
        for month, snapshot in sorted(latest_by_month.items())
    ]
