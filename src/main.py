from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.urls import api_router
from core.config import get_settings


settings = get_settings()


app = FastAPI(
    title=settings.PROJECT_NAME,
    servers=[
        {"url": settings.SERVER_HOST},
    ],
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=ORJSONResponse,
    debug=settings.DEBUG,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
