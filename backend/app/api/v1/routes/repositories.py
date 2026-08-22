from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.integrations.github.client import GitHubClient
from app.integrations.github.exceptions import GitHubRepositoryNotFoundError
from app.schemas.repository import (
    RepositoryAnalysisRequest,
    RepositoryCommitActivityResponse,
    RepositoryLanguagesResponse,
    RepositoryMetadataResponse,
    RepositoryTrackResponse,
)
from app.services.repository_analysis import (
    calculate_commit_activity,
    calculate_language_breakdown,
)
from app.services.repository_tracking import track_repository
from app.utils.github import extract_github_repository


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.post("/validate")
async def validate_repository(
    request: RepositoryAnalysisRequest,
) -> dict[str, str | bool]:
    """
    Validate and normalize a GitHub repository URL.

    Pydantic validates the incoming request before this function runs,
    so reaching this point means the repository URL passed validation.
    """

    return {
        "repository_url": request.repository_url,
        "valid": True,
    }


@router.post(
    "/metadata",
    response_model=RepositoryMetadataResponse,
)
async def get_repository_metadata(
    request: RepositoryAnalysisRequest,
) -> RepositoryMetadataResponse:
    """
    Validate a GitHub repository URL and fetch its metadata from GitHub.
    """

    # Extract the repository owner and name from the validated URL.
    owner, repository = extract_github_repository(
        request.repository_url
    )

    # Create the client responsible for communicating with GitHub.
    github_client = GitHubClient()

    try:
        # Fetch the raw repository information asynchronously from GitHub.
        repository_data = await github_client.get_repository(
            owner=owner,
            repository=repository,
        )

    except GitHubRepositoryNotFoundError as exc:
        # Convert the internal GitHub error into an HTTP 404 response.
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # Convert GitHub's large raw response into RepoPulse's
    # smaller and stable repository metadata response.
    return RepositoryMetadataResponse(
        # Basic repository information
        id=repository_data["id"],
        name=repository_data["name"],
        full_name=repository_data["full_name"],
        description=repository_data.get("description"),
        repository_url=repository_data["html_url"],

        # Repository owner
        owner=repository_data["owner"]["login"],
        owner_avatar_url=repository_data["owner"]["avatar_url"],

        # Repository statistics
        stars=repository_data["stargazers_count"],
        forks=repository_data["forks_count"],
        watchers=repository_data["watchers_count"],
        open_issues=repository_data["open_issues_count"],

        # Technical information
        language=repository_data.get("language"),
        topics=repository_data.get("topics", []),
        default_branch=repository_data["default_branch"],

        # Repository state
        license=(
            repository_data["license"]["spdx_id"]
            if repository_data.get("license")
            else None
        ),
        is_fork=repository_data["fork"],
        archived=repository_data["archived"],
        visibility=repository_data["visibility"],

        # Repository activity timestamps
        created_at=repository_data["created_at"],
        updated_at=repository_data["updated_at"],
        pushed_at=repository_data["pushed_at"],
    )


@router.post(
    "/languages",
    response_model=RepositoryLanguagesResponse,
)
async def get_repository_languages(
        request: RepositoryAnalysisRequest,
)-> RepositoryLanguagesResponse:
    """
    Fetch and analyze the programming languages used
    in a GitHub repository.
    """

    # The repository URL has already been validated and normalized.
    owner, repository = extract_github_repository(
        request.repository_url
    )

    github_client = GitHubClient()

    try:
        # Fetch raw language byte counts from GitHub.
        language_bytes = await github_client.get_repository_languages(
            owner=owner,
            repository=repository,
        )

    except GitHubRepositoryNotFoundError as exc:
        #Convert the internal GitHub error into an HTTP 404 Response.
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


    #Convert GitHub's byte counts into Repopulse percentages
    return calculate_language_breakdown(language_bytes)



@router.post(
    "/activity",
    response_model=RepositoryCommitActivityResponse,
)
async def get_repository_activity(
        request: RepositoryAnalysisRequest,
) -> RepositoryCommitActivityResponse:
    """
    Fetch recent repository commits and calculate
    basic commit activity metrics
    """

    #Extract owner and repository name from the validated GitHub URL.
    owner, repository = extract_github_repository(
        request.repository_url
    )

    since = datetime.now(timezone.utc) - timedelta(days=30)

    github_client = GitHubClient()

    try:
        #Fetch recent commit data from GitHub
        commits = await github_client.get_repository_commits(
            owner=owner,
            repository=repository,
            since=since,
        )

    except GitHubRepositoryNotFoundError as exc:
        #Convert our internal GitHub error into an HTTP 404 response.
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # Convert raw GitHub commits into RepoPulse activity metrics
    return calculate_commit_activity(commits)


@router.post(
    "/track",
    response_model=RepositoryTrackResponse,
)
async def track_github_repository(
        request:RepositoryAnalysisRequest,
        db: Session = Depends(get_db),
) -> RepositoryTrackResponse:
    """
    Verify GitHub repository and store it for RepoPulse tracking
    """

    owner, repository = extract_github_repository(
        request.repository_url
    )

    github_client = GitHubClient()

    try:
        # Verify the repository actually exists on GitHub.
        repository_data = await github_client.get_repository(
            owner=owner,
            repository=repository,
        )

    except GitHubRepositoryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    tracked_repository, created = track_repository(
        db=db,
        github_owner=repository_data["owner"]["login"],
        github_name=repository_data["name"],
        repository_url=repository_data["html_url"],
    )

    return RepositoryTrackResponse(
        id=tracked_repository.id,
        repository_url=tracked_repository.repository_url,
        github_owner=tracked_repository.github_owner,
        github_name=tracked_repository.github_name,
        is_tracked=tracked_repository.is_tracked,
        created_at=tracked_repository.created_at,
    )







































