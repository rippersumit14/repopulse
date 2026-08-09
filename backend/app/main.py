from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


# Allow the configured React frontend to communicate with this API
# when the browser considers the frontend and backend different origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register operational and versioned business routes.
app.include_router(router)