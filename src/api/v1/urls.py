from fastapi import APIRouter

from api.v1.endpoints import films, genres, health, persons


api_router = APIRouter()

api_router.include_router(
    router=films.router,
    prefix="/films",
    tags=["films"],
)
api_router.include_router(
    router=genres.router,
    prefix="/genres",
    tags=["genres"],
)
api_router.include_router(
    router=persons.router,
    prefix="/persons",
    tags=["persons"],
)

# Healthcheck
api_router.include_router(
    router=health.router,
    prefix="/healthcheck",
    tags=["health"],
)
