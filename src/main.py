import aioredis
from elasticsearch import AsyncElasticsearch

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.urls import api_router
from core.config import get_settings
from db import elastic, redis


settings = get_settings()


app = FastAPI(
    title=settings.PROJECT_NAME,
    servers=[
        {"url": server_host}
        for server_host in settings.SERVER_HOSTS
    ],
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=ORJSONResponse,
    debug=settings.DEBUG,
)


@app.on_event("startup")
async def startup():
    elastic.es = AsyncElasticsearch(
        hosts=[
            {"host": settings.ES_HOST, "port": settings.ES_PORT},
        ],
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    redis.redis = await aioredis.from_url(
        url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=settings.REDIS_RESP,
    )


@app.on_event("shutdown")
async def shutdown():
    await elastic.es.close()
    await redis.redis.close()


app.include_router(api_router, prefix=settings.API_V1_STR)
