from pydantic import BaseModel, Field, field_validator


class RepositoryAnalysisRequest(BaseModel):
    """
    Data required to start a repository analysis.
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

        # RepoPulse currently supports only standard HTTPS GitHub URLs.
        if not value.startswith(github_prefix):
            raise ValueError(
                "Repository URL must start with https://github.com/"
            )

        # Remove the GitHub domain so only "owner/repository" remains.
        repository_path = value.removeprefix(github_prefix)

        # Remove a trailing slash to normalize equivalent URLs.
        repository_path = repository_path.rstrip("/")

        # Git clone URLs may end in ".git"; treat them as the same repository.
        if repository_path.endswith(".git"):
            repository_path = repository_path.removesuffix(".git")

        # A repository path must contain exactly:
        # owner/repository
        parts = repository_path.split("/")

        if len(parts) != 2:
            raise ValueError(
                "URL must point to a GitHub repository in owner/repository format."
            )

        owner, repository = parts

        # Both parts must contain an actual value.
        if not owner or not repository:
            raise ValueError(
                "GitHub repository owner and repository name are required."
            )

        # Return one consistent URL format for the rest of the application.
        return f"{github_prefix}{owner}/{repository}"