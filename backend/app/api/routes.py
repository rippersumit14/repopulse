from fastapi import APIRouter

from app.api.v1.router import api_router as v1_router
from app.api.v1.routes.health import router as health_router


router = APIRouter()

# Operational endpoints remain independent of business API versioning.
router.include_router(health_router)

# Product endpoints are grouped under the versioned API namespace.
router.include_router(v1_router)