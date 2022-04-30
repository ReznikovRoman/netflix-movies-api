from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest
from elasticsearch import AsyncElasticsearch

from .testdata.elastic import ES_DSNS
from .testlib import create_anon_client, setup_elastic, teardown_elastic


if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from .testlib import APIClient


pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def api_client() -> APIClient:
    anon_client = create_anon_client()
    yield anon_client
    await anon_client.close()


@pytest.fixture
async def elastic() -> AsyncElasticsearch:
    await setup_elastic()
    yield AsyncElasticsearch(
        hosts=ES_DSNS,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    await teardown_elastic()
