from datetime import datetime, timezone

from app.schemas.repository import (
    LanguageBreakdown,
    RepositoryCommitActivityResponse,
    RepositoryLanguagesResponse,
)


def calculate_language_breakdown(
    language_bytes: dict[str, int],
) -> RepositoryLanguagesResponse:
    """
    Convert GitHub language byte counts into a structured
    RepoPulse language breakdown with percentages.
    """

    # Calculate the total number of bytes across all detected languages.
    total_bytes = sum(language_bytes.values())

    # Some repositories may not have any detected programming languages.
    if total_bytes == 0:
        return RepositoryLanguagesResponse(
            total_bytes=0,
            languages=[],
        )

    languages: list[LanguageBreakdown] = []

    for language_name, bytes_count in language_bytes.items():
        # Calculate the percentage of the repository for this language.
        percentage = (bytes_count / total_bytes) * 100

        languages.append(
            LanguageBreakdown(
                name=language_name,
                bytes=bytes_count,
                percentage=round(percentage, 2),
            )
        )

    # Show the most-used languages first.
    languages.sort(
        key=lambda language: language.percentage,
        reverse=True,
    )

    return RepositoryLanguagesResponse(
        total_bytes=total_bytes,
        languages=languages,
    )


def calculate_commit_activity(
    commits: list[dict],
) -> RepositoryCommitActivityResponse:
    """
    Analyze recent GitHub commits and calculate
    basic repository activity metrics.
    """

    now = datetime.now(timezone.utc)

    commits_last_7_days = 0
    commits_last_30_days = 0

    last_commit_at: datetime | None = None

    for commit_data in commits:
        # GitHub stores the commit timestamp inside:
        # commit -> author -> date
        commit_date_raw = (
            commit_data
            .get("commit", {})
            .get("author", {})
            .get("date")
        )

        if not commit_date_raw:
            continue

        # Convert GitHub's ISO timestamp into a Python datetime.
        commit_date = datetime.fromisoformat(
            commit_date_raw.replace("Z", "+00:00")
        )

        # GitHub returns commits newest first, so the first valid
        # timestamp is the most recent commit.
        if last_commit_at is None:
            last_commit_at = commit_date

        age_days = (now - commit_date).days

        if age_days <= 7:
            commits_last_7_days += 1

        if age_days <= 30:
            commits_last_30_days += 1

    days_since_last_commit: int | None = None

    if last_commit_at is not None:
        days_since_last_commit = (now - last_commit_at).days

    # Simple first version of activity classification.
    if commits_last_30_days >= 20:
        activity_level = "high"
    elif commits_last_30_days >= 5:
        activity_level = "medium"
    else:
        activity_level = "low"

    return RepositoryCommitActivityResponse(
        total_recent_commits=len(commits),
        commits_last_7_days=commits_last_7_days,
        commits_last_30_days=commits_last_30_days,
        last_commit_at=last_commit_at,
        days_since_last_commit=days_since_last_commit,
        activity_level=activity_level,
    )
