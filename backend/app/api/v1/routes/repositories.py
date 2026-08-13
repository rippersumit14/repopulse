from fastapi import APIRouter, HTTPException
from app.integrations.github.client import GitHubClient
from app.integrations.github.exceptions import GitHubRepositoryNotFoundError
from app.schemas.repository import RepositoryAnalysisRequest
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
    Validate and normalize a GitHub Repository URl.

    Pydantic validates the incoming request before this function runs,
    so reaching this point means the repository URL passed validation
    """

    return {
        "repository_url": request.repository_url,
        "valid": True,
    }

@router.post("/metadata")
async def get_repository_metadata(
        request: RepositoryAnalysisRequest,
) -> dict:
    """
    Validate a GitHub repo URL and fetch its metadata from GitHub
    """
    
    #The pydantic validator has already cleaned and validated the URL
    owner, repository = extract_github