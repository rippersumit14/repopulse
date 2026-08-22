from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RepositoryAnalysisRequest(BaseModel):
    """
    Data required from the client to start a repository analysis.

    The client only needs to provide the public GitHub repository URL.
    """

    repository_url: str = Field(
        ...,
        min_length=1,
        description="Public GitHub repository URL to analyze.",
        examples=["https://github.com/fastapi/fastapi"],
    )

    @field_validator("repository_url")
    @classmethod
    def validate_repository_url(cls, value: str) -> str:
        """
        Validate and normalize a GitHub repository URL.
        """

        # Remove accidental spaces from the beginning and end.
        value = value.strip()

        github_prefix = "https://github.com/"

        # RepoPulse currently accepts only standard HTTPS GitHub URLs.
        if not value.startswith(github_prefix):
            raise ValueError(
                "Repository URL must start with https://github.com/"
            )

        # Remove the GitHub domain and keep only "owner/repository".
        repository_path = value.removeprefix(github_prefix)

        # Normalize URLs that contain a trailing slash.
        repository_path = repository_path.rstrip("/")

        # Treat Git clone URLs ending in ".git" as normal repository URLs.
        if repository_path.endswith(".git"):
            repository_path = repository_path.removesuffix(".git")

        # A valid repository path must contain exactly:
        # owner/repository
        parts = repository_path.split("/")

        if len(parts) != 2:
            raise ValueError(
                "URL must point to a GitHub repository "
                "in owner/repository format."
            )

        owner, repository = parts

        # Both the owner and repository name must contain a value.
        if not owner or not repository:
            raise ValueError(
                "GitHub repository owner and repository name are required."
            )

        # Return one normalized URL format for the rest of RepoPulse.
        return f"{github_prefix}{owner}/{repository}"


class RepositoryMetadataResponse(BaseModel):
    """
    Clean repository metadata returned by the RepoPulse API.

    This model prevents clients from depending directly on
    GitHub's raw API response structure.
    """

    # Basic repository information
    id: int
    name: str
    full_name: str
    description: str | None = None
    repository_url: str

    # Repository owner
    owner: str
    owner_avatar_url: str

    # Repository statistics
    stars: int
    forks: int
    watchers: int
    open_issues: int

    # Technical information
    language: str | None = None
    topics: list[str]
    default_branch: str

    # Repository state
    license: str | None = None
    is_fork: bool
    archived: bool
    visibility: str

    # Repository activity timestamps
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime


class LanguageBreakdown(BaseModel):
    """
    Information about one programming language detected in a GitHub repository.
    """

    name: str
    bytes: int
    percentage: float


class RepositoryLanguagesResponse(BaseModel):
    """Language composition of a GitHub repository."""

    total_bytes: int
    languages: list[LanguageBreakdown]


class RepositoryCommitActivityResponse(BaseModel):
    """
    Commit activity summary for a GitHub Repository.

    These fields are calculated by RepoPulse from recent
    GitHub commit data.
    """

    total_recent_commits: int
    commits_last_7_days: int
    commits_last_30_days: int

    last_commit_at: datetime | None = None
    days_since_last_commit: int | None = None

    activity_level: str


class RepositoryTrackResponse(BaseModel):
    """
    Repository successfully registered for tracking.
    """

    id: int
    repository_url: str
    github_owner: str
    github_name: str
    is_tracked: bool
    created_at: datetime


class HealthScoreResponse(BaseModel):
    """
    Explainable deterministic health score for a repository analysis.
    """

    overall_score: int
    activity_score: int
    maintenance_score: int
    reasons: list[str]


class RepositoryAnalysisResponse(BaseModel):
    """
    Result returned after a tracked repository is manually analyzed.
    """

    repository_id: int
    repository: RepositoryMetadataResponse
    languages: RepositoryLanguagesResponse
    activity: RepositoryCommitActivityResponse
    health_score: HealthScoreResponse
    snapshot_id: int
    analyzed_at: datetime


class AnalysisSnapshotResponse(BaseModel):
    """Stored point-in-time analysis row exposed if needed by future routes."""

    id: int
    repository_id: int
    stars: int
    forks: int
    open_issues: int
    contributors_count: int
    commits_last_7_days: int
    commits_last_30_days: int
    activity_level: str
    health_score: float | None
    analyzed_at: datetime


HistoryRange = Literal["7d", "30d", "12m"]


class RepositoryHistoryPoint(BaseModel):
    """Chart-ready point for repository history graphs."""

    date: date
    health_score: float | None
    commits_last_30_days: int
    stars: int
    open_issues: int


class RepositoryHistoryResponse(BaseModel):
    """History response for one requested chart range."""

    range: HistoryRange
    points: list[RepositoryHistoryPoint]
