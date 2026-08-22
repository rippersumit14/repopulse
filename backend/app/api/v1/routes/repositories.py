from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.dependencies import get_db
from app.integrations.github.client import GitHubClient
from app.integrations.github.exceptions import GitHubRepositoryNotFoundError
from app.models.repository import Repository
from app.models.user import User
from app.schemas.repository import (
    HistoryRange,
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
    RepositoryCommitActivityResponse,
    RepositoryHistoryResponse,
    RepositoryLanguagesResponse,
    RepositoryMetadataResponse,
    RepositoryTrackResponse,
)
from app.services.repository_analyzer import (
    analyze_repository,
    map_repository_metadata,
)
from app.services.repository_analysis import (
    calculate_commit_activity,
    calculate_language_breakdown,
)
from app.services.repository_tracking import (
    track_repository_for_user,
    user_tracks_repository,
)
from app.services.snapshots import (
    build_history_points,
    create_snapshot,
    get_repository_snapshots,
)
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

    return map_repository_metadata(repository_data)


@router.post(
    "/languages",
    response_model=RepositoryLanguagesResponse,
)
async def get_repository_languages(
    request: RepositoryAnalysisRequest,
) -> RepositoryLanguagesResponse:
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
        # Convert the internal GitHub error into an HTTP 404 response.
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # Convert GitHub's byte counts into RepoPulse percentages.
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

    # Extract owner and repository name from the validated GitHub URL.
    owner, repository = extract_github_repository(
        request.repository_url
    )

    since = datetime.now(timezone.utc) - timedelta(days=30)

    github_client = GitHubClient()

    try:
        # Fetch recent commit data from GitHub.
        commits = await github_client.get_repository_commits(
            owner=owner,
            repository=repository,
            since=since,
        )

    except GitHubRepositoryNotFoundError as exc:
        # Convert our internal GitHub error into an HTTP 404 response.
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
    request: RepositoryAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepositoryTrackResponse:
    """
    Verify GitHub repository and track it for the authenticated user.
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
            detail=str(exc),
        ) from exc

    tracked_repository, _, _ = track_repository_for_user(
        db=db,
        user=current_user,
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


@router.post(
    "/{repository_id}/analyze",
    response_model=RepositoryAnalysisResponse,
)
async def analyze_tracked_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepositoryAnalysisResponse:
    """
    Manually analyze a repository tracked by the authenticated user.
    """

    repository = db.get(Repository, repository_id)

    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracked repository was not found.",
        )

    if not user_tracks_repository(
        db=db,
        user_id=current_user.id,
        repository_id=repository_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not track this repository.",
        )

    try:
        analysis = await analyze_repository(
            owner=repository.github_owner,
            repository=repository.github_name,
        )
    except GitHubRepositoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    snapshot = create_snapshot(
        db=db,
        repository_id=repository.id,
        stars=analysis.metadata.stars,
        forks=analysis.metadata.forks,
        open_issues=analysis.metadata.open_issues,
        contributors_count=0,
        commits_last_7_days=analysis.activity.commits_last_7_days,
        commits_last_30_days=analysis.activity.commits_last_30_days,
        activity_level=analysis.activity.activity_level,
        health_score=analysis.health_score.overall_score,
    )

    repository.last_analyzed_at = snapshot.analyzed_at

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return RepositoryAnalysisResponse(
        repository_id=repository.id,
        repository=analysis.metadata,
        languages=analysis.languages,
        activity=analysis.activity,
        health_score=analysis.health_score,
        snapshot_id=snapshot.id,
        analyzed_at=snapshot.analyzed_at,
    )


@router.get(
    "/{repository_id}/history",
    response_model=RepositoryHistoryResponse,
)
def get_repository_history(
    repository_id: int,
    history_range: HistoryRange = Query(default="7d", alias="range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepositoryHistoryResponse:
    """
    Return chart-ready snapshot history for a repository the user tracks.
    """

    repository = db.get(Repository, repository_id)

    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracked repository was not found.",
        )

    if not user_tracks_repository(
        db=db,
        user_id=current_user.id,
        repository_id=repository_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not track this repository.",
        )

    snapshots = get_repository_snapshots(
        db=db,
        repository_id=repository_id,
        history_range=history_range,
    )

    return RepositoryHistoryResponse(
        range=history_range,
        points=build_history_points(
            snapshots,
            history_range=history_range,
        ),
    )







































