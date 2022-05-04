from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

import aioredis.sentinel
import backoff
import elasticsearch
import orjson
from aiohttp import ClientSession

from .settings import get_settings
from .testdata.elastic import ES_GENRE_MAPPING, ES_INDEX_SETTINGS, ES_MOVIES_MAPPING, ES_PERSON_MAPPING


if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from aioredis import Redis

    APIResponse = Union[dict, str, list[dict], dict[str, Any]]


settings = get_settings()


elastic_schemas = {
    "movies": ES_MOVIES_MAPPING,
    "genre": ES_GENRE_MAPPING,
    "person": ES_PERSON_MAPPING,
}


class APIClient(ClientSession):
    """Aiohttp клиент для тестов."""

    def __init__(self, base_url: str = "http://localhost:8001", *args, **kwargs):
        self.base_url = base_url
        super().__init__(base_url, *args, **kwargs)

    async def get(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("get", kwargs.get("expected_status_code", 200), *args, **kwargs)

    async def post(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("post", kwargs.get("expected_status_code", 201), *args, **kwargs)

    async def put(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("put", kwargs.get("expected_status_code", 200), *args, **kwargs)

    async def patch(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("patch", kwargs.get("expected_status_code", 200), *args, **kwargs)

    async def delete(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("delete", kwargs.get("expected_status_code", 204), *args, **kwargs)

    async def _api_call(self, method: str, expected: int, *args, **kwargs) -> APIResponse:
        kwargs.pop("expected_status_code", None)
        as_response = kwargs.pop("as_response", False)

        method = getattr(super(), method)
        response = await method(*args, **kwargs)

        if as_response:
            return response

        content = await self._decode(response)

        error_message = f"Got {response.status} instead of {expected}. Content is '{content}'"
        assert response.status == expected, error_message

        return content

    async def _decode(self, response: ClientResponse) -> APIResponse:
        content = await response.content.read()
        decoded = content.decode("utf-8", errors="ignore")
        if self.is_json(response):
            return orjson.loads(decoded)
        return decoded

    @staticmethod
    def is_json(response: ClientResponse) -> bool:
        if response.headers:
            return "json" in response.headers.get("content-type")
        return False


def create_anon_client() -> APIClient:
    return APIClient(base_url=settings.CLIENT_BASE_URL)


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=elasticsearch.exceptions.ConnectionError,
    max_tries=5,
    max_time=2 * 60,
)
async def setup_elastic() -> elasticsearch.AsyncElasticsearch:
    elastic = elasticsearch.AsyncElasticsearch(
        hosts=[
            {"host": settings.ES_HOST, "port": settings.ES_PORT},
        ],
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    for index_name, mapping in elastic_schemas.items():
        body = {
            "settings": ES_INDEX_SETTINGS,
            "mappings": mapping,
        }
        await elastic.indices.create(index=index_name, body=body)
    return elastic


async def teardown_elastic() -> None:
    elastic = elasticsearch.AsyncElasticsearch(
        hosts=[
            {"host": settings.ES_HOST, "port": settings.ES_PORT},
        ],
        max_retries=30,
        retry_on_timeout=True,
        request_timeout=30,
    )
    for index_name in elastic_schemas.keys():
        await elastic.indices.delete(index=index_name)
    await elastic.close()


async def flush_redis_cache() -> None:
    sentinel = aioredis.sentinel.Sentinel(
        sentinels=[(sentinel, 26379) for sentinel in settings.REDIS_SENTINELS],
        socket_timeout=0.5,
    )
    master: Redis = await sentinel.master_for(
        service_name=settings.REDIS_MASTER_SET,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        password=settings.REDIS_PASSWORD,
    )
    await master.flushdb()
