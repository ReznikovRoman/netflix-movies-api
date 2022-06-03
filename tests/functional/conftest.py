from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from .settings import get_settings
from .testlib import create_anon_client, flush_redis_cache, setup_elastic, teardown_elastic


if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from elasticsearch import AsyncElasticsearch

    from .settings import Test
    from .testlib import APIClient

pytestmark = [pytest.mark.asyncio]

settings_ = get_settings()


@pytest.fixture
def settings() -> Test:
    return settings_


@pytest.fixture(autouse=True)
async def _autoflush_cache() -> None:
    try:
        yield
    finally:
        await flush_redis_cache()


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> APIClient:
    anon_client = create_anon_client()
    yield anon_client
    await anon_client.close()


@pytest.fixture
async def elastic() -> AsyncElasticsearch:
    client = await setup_elastic()
    yield client
    await teardown_elastic()
