from fastapi import APIRouter

router = APIRouter(
    tags=["Health"],
)

@router.get("/health")
async def health_check() -> dict[str, str]:
    '''
    Check whether the RepoPulse API is running

    This endpoint can later be used by deployment platform,
    monitoring systems, and container health checks
    :return:
    '''
    return {"status": "ok"}

