from fastapi import APIRouter

from api.v1.endpoints import homepage


api_router = APIRouter()

api_router.include_router(
    router=homepage.router,
    prefix="/home",
    tags=["homepage"],
)
