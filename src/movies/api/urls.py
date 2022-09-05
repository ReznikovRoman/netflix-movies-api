from fastapi import APIRouter

from .v1.urls import api_v1_router

api_router = APIRouter(prefix="/api")

api_router.include_router(api_v1_router)
