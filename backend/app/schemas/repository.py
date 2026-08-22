from datetime import datetime
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
    #Language Composition of a GitHub Repo
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







































