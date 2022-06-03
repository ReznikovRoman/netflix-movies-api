import aioredis
import aioredis.sentinel
from elasticsearch import AsyncElasticsearch

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.urls import api_router
from core.config import get_settings
from db import elastic, redis_sentinel


settings = get_settings()


app = FastAPI(
    title="Netflix Movies API v1",
    description="АПИ сервиса фильмов для онлайн-кинотеатра",
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
    redis_sentinel.redis_sentinel = aioredis.sentinel.Sentinel(
        sentinels=[(sentinel, 26379) for sentinel in settings.REDIS_SENTINELS],
        socket_timeout=0.5,
    )
    elastic.es = AsyncElasticsearch(
        hosts=[
            {"host": settings.ES_HOST, "port": settings.ES_PORT},
        ],
        max_retries=30,
        retry_on_timeout=settings.ES_RETRY_ON_TIMEOUT,
        request_timeout=30,
    )


@app.on_event("shutdown")
async def shutdown():
    for sentinel in redis_sentinel.redis_sentinel.sentinels:
        await sentinel.close()
    await elastic.es.close()


app.include_router(api_router, prefix=settings.API_V1_STR)
