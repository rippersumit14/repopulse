from datetime import datetime, timedelta, timezone

from app.services.health_score import calculate_health_score
from app.services.repository_analysis import (
    calculate_commit_activity,
    calculate_language_breakdown,
)
from app.schemas.repository import RepositoryCommitActivityResponse, RepositoryMetadataResponse


def make_commit(days_ago: int) -> dict:
    commit_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

    return {
        "commit": {
            "author": {
                "date": commit_date.isoformat().replace("+00:00", "Z"),
            },
        },
    }


def test_language_breakdown_calculates_percentages() -> None:
    result = calculate_language_breakdown(
        {
            "Python": 300,
            "TypeScript": 100,
        }
    )

    assert result.total_bytes == 400
    assert result.languages[0].name == "Python"
    assert result.languages[0].percentage == 75.0
    assert result.languages[1].percentage == 25.0


def test_language_breakdown_handles_empty_response() -> None:
    result = calculate_language_breakdown({})

    assert result.total_bytes == 0
    assert result.languages == []


def test_commit_activity_classifies_active_repository() -> None:
    result = calculate_commit_activity(
        [
            *[make_commit(1) for _ in range(6)],
            *[make_commit(20) for _ in range(15)],
        ]
    )

    assert result.commits_last_7_days == 6
    assert result.commits_last_30_days == 21
    assert result.activity_level == "high"


def test_commit_activity_handles_no_commits() -> None:
    result = calculate_commit_activity([])

    assert result.total_recent_commits == 0
    assert result.commits_last_7_days == 0
    assert result.commits_last_30_days == 0
    assert result.activity_level == "low"
    assert result.last_commit_at is None


def test_health_score_is_deterministic() -> None:
    metadata = RepositoryMetadataResponse(
        id=1,
        name="repo",
        full_name="owner/repo",
        description=None,
        repository_url="https://github.com/owner/repo",
        owner="owner",
        owner_avatar_url="https://example.com/avatar.png",
        stars=10,
        forks=2,
        watchers=10,
        open_issues=3,
        language="Python",
        topics=[],
        default_branch="main",
        license="MIT",
        is_fork=False,
        archived=False,
        visibility="public",
        created_at=datetime.now(timezone.utc) - timedelta(days=365),
        updated_at=datetime.now(timezone.utc),
        pushed_at=datetime.now(timezone.utc),
    )
    activity = RepositoryCommitActivityResponse(
        total_recent_commits=10,
        commits_last_7_days=2,
        commits_last_30_days=10,
        last_commit_at=datetime.now(timezone.utc),
        days_since_last_commit=0,
        activity_level="medium",
    )

    first = calculate_health_score(metadata=metadata, activity=activity)
    second = calculate_health_score(metadata=metadata, activity=activity)

    assert first == second
    assert first.overall_score > 0
    assert first.reasons
