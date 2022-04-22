from fastapi import APIRouter

from api.v1.endpoints import films, genres, homepage


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

# Temp `homepage` route
api_router.include_router(
    router=homepage.router,
    prefix="/home",
    tags=["homepage"],
)
