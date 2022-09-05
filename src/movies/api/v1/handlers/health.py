from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/", summary="'Здоровье' сервиса")
async def healthcheck():
    """Проверка состояния сервиса."""
    return {"status": "ok"}
