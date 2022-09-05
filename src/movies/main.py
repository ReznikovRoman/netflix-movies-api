import logging

import aioredis
import aioredis.sentinel
from elasticsearch import AsyncElasticsearch

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from movies.api.urls import api_router
from movies.common.exceptions import NetflixMoviesError
from movies.core.config import get_settings
from movies.db import elastic, redis_sentinel

from .containers import Container, override_providers

settings = get_settings()


def create_app() -> FastAPI:
    """Фабрика по созданию приложения FastAPI."""
    container = Container()
    container.config.from_pydantic(settings=settings)
    container = override_providers(container)

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

    @app.exception_handler(NetflixMoviesError)
    async def project_exception_handler(_: Request, exc: NetflixMoviesError):
        return ORJSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.on_event("startup")
    async def startup():
        await container.init_resources()
        container.check_dependencies()
        logging.info("Start server")
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
        await container.shutdown_resources()
        logging.info("Cleanup resources")
        for sentinel in redis_sentinel.redis_sentinel.sentinels:
            await sentinel.close()
        await elastic.es.close()

    app.container = container
    app.include_router(api_router)
    return app
