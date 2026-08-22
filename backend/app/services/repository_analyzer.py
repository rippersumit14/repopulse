from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

from app.integrations.github.client import GitHubClient
from app.schemas.repository import (
    HealthScoreResponse,
    RepositoryCommitActivityResponse,
    RepositoryLanguagesResponse,
    RepositoryMetadataResponse,
)
from app.services.health_score import calculate_health_score
from app.services.repository_analysis import (
    calculate_commit_activity,
    calculate_language_breakdown,
)


@dataclass(frozen=True)
class RepositoryAnalysisResult:
    """Single in-memory object containing every part of one analysis run."""

    metadata: RepositoryMetadataResponse
    languages: RepositoryLanguagesResponse
    activity: RepositoryCommitActivityResponse
    health_score: HealthScoreResponse


def map_repository_metadata(repository_data: dict) -> RepositoryMetadataResponse:
    """
    Convert GitHub's raw repository JSON into RepoPulse's stable API schema.

    Keeping this mapping in one place prevents routes and background jobs from
    depending directly on GitHub field names.
    """

    return RepositoryMetadataResponse(
        id=repository_data["id"],
        name=repository_data["name"],
        full_name=repository_data["full_name"],
        description=repository_data.get("description"),
        repository_url=repository_data["html_url"],
        owner=repository_data["owner"]["login"],
        owner_avatar_url=repository_data["owner"]["avatar_url"],
        stars=repository_data["stargazers_count"],
        forks=repository_data["forks_count"],
        watchers=repository_data["watchers_count"],
        open_issues=repository_data["open_issues_count"],
        language=repository_data.get("language"),
        topics=repository_data.get("topics", []),
        default_branch=repository_data["default_branch"],
        license=(
            repository_data["license"]["spdx_id"]
            if repository_data.get("license")
            else None
        ),
        is_fork=repository_data["fork"],
        archived=repository_data["archived"],
        visibility=repository_data["visibility"],
        created_at=repository_data["created_at"],
        updated_at=repository_data["updated_at"],
        pushed_at=repository_data["pushed_at"],
    )


async def analyze_repository(
    *,
    owner: str,
    repository: str,
    github_client: GitHubClient | None = None,
) -> RepositoryAnalysisResult:
    """
    Orchestrate a full repository analysis using internal Python services.

    This intentionally does not call RepoPulse HTTP endpoints, so scheduled jobs
    and manual routes can reuse the same analysis path later.
    """

    client = github_client or GitHubClient()
    since = datetime.now(timezone.utc) - timedelta(days=30)

    repository_data = await client.get_repository(
        owner=owner,
        repository=repository,
    )
    # GitHub returns language byte counts separately from repository metadata.
    language_bytes = await client.get_repository_languages(
        owner=owner,
        repository=repository,
    )
    # Recent commit data drives activity metrics and part of the health score.
    commits = await client.get_repository_commits(
        owner=owner,
        repository=repository,
        since=since,
    )

    metadata = map_repository_metadata(repository_data)
    languages = calculate_language_breakdown(language_bytes)
    activity = calculate_commit_activity(commits)
    health_score = calculate_health_score(
        metadata=metadata,
        activity=activity,
    )

    return RepositoryAnalysisResult(
        metadata=metadata,
        languages=languages,
        activity=activity,
        health_score=health_score,
    )
