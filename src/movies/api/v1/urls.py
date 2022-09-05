from fastapi import APIRouter

from movies.api.v1.handlers import films, genres, health, persons

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(router=films.router, prefix="/films")
api_v1_router.include_router(router=genres.router, prefix="/genres")
api_v1_router.include_router(router=persons.router, prefix="/persons")

# Healthcheck
api_v1_router.include_router(router=health.router, prefix="/healthcheck")
