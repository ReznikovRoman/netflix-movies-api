from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/", summary="Service health")
async def healthcheck():
    """Check service health."""
    raise Exception()
    return {"status": "ok"}
