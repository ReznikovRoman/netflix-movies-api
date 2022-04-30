import asyncio

import pytest
from elasticsearch import AsyncElasticsearch

from .testdata.elastic import ES_DSNS
from .testlib import create_anon_client, setup_elastic, teardown_elastic


pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def api_client():
    anon_client = create_anon_client()
    yield anon_client
    await anon_client.close()


@pytest.fixture
async def elastic():
    await setup_elastic()
    yield AsyncElasticsearch(
        hosts=ES_DSNS,
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    await teardown_elastic()
