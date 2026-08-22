from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.repositories import router as repositories_router


# All version-1 product endpoints are grouped under /api/v1.
api_router = APIRouter(prefix="/api/v1")


# Register repository-related endpoints with API version 1.
api_router.include_router(auth_router)
api_router.include_router(repositories_router)
