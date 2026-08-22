from datetime import datetime, timezone

from app.schemas.repository import (
    HealthScoreResponse,
    RepositoryCommitActivityResponse,
    RepositoryMetadataResponse,
)


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def calculate_health_score(
    *,
    metadata: RepositoryMetadataResponse,
    activity: RepositoryCommitActivityResponse,
) -> HealthScoreResponse:
    """
    Calculate a deterministic V1 health score from currently available signals.

    Unsupported future dimensions are intentionally not included.
    """

    reasons: list[str] = []

    if activity.commits_last_30_days >= 20:
        activity_score = 95
        reasons.append("High commit activity in the last 30 days.")
    elif activity.commits_last_30_days >= 5:
        activity_score = 75
        reasons.append("Moderate commit activity in the last 30 days.")
    elif activity.commits_last_30_days > 0:
        activity_score = 55
        reasons.append("Some recent commit activity was detected.")
    else:
        activity_score = 25
        reasons.append("No recent commits were detected.")

    maintenance_score = 100

    if metadata.archived:
        maintenance_score -= 45
        reasons.append("Repository is archived.")
    else:
        reasons.append("Repository is not archived.")

    if metadata.license:
        reasons.append("Repository has a license.")
    else:
        maintenance_score -= 15
        reasons.append("No license was detected.")

    days_since_push = (
        datetime.now(timezone.utc) - metadata.pushed_at
    ).days

    if days_since_push <= 30:
        reasons.append("Repository was pushed recently.")
    elif days_since_push <= 180:
        maintenance_score -= 10
        reasons.append("Repository has not been pushed in the last 30 days.")
    else:
        maintenance_score -= 25
        reasons.append("Repository appears stale based on last push date.")

    if metadata.open_issues > 100:
        maintenance_score -= 10
        reasons.append("Repository has a large number of open issues.")

    maintenance_score = clamp_score(maintenance_score)
    overall_score = clamp_score(
        round((activity_score * 0.55) + (maintenance_score * 0.45))
    )

    return HealthScoreResponse(
        overall_score=overall_score,
        activity_score=activity_score,
        maintenance_score=maintenance_score,
        reasons=reasons,
    )
