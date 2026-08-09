from fastapi import APIRouter
from app.schemas.repository import RepositoryAnalysisRequest

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
