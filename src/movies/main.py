import logging

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from movies.api.urls import api_router
from movies.common.exceptions import NetflixMoviesError
from movies.core.config import get_settings

from .containers import Container, override_providers

settings = get_settings()


def create_app() -> FastAPI:  # 123
    """FastAPI app factory."""  # noqa: D403
    container = Container()
    container.config.from_pydantic(settings=settings)
    container = override_providers(container)

    app = FastAPI(
        title="Netflix Movies API v1",
        description="Netflix Movies API",
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

    @app.on_event("shutdown")
    async def shutdown():
        await container.shutdown_resources()
        logging.info("Cleanup resources")

    app.container = container
    app.include_router(api_router)
    return app
