from __future__ import annotations

import base64
import hashlib
import json
from typing import TYPE_CHECKING, ClassVar

from aioredis import Redis
from elasticsearch.exceptions import NotFoundError as ElasticNotFoundError

from common.exceptions import NotFoundError


if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch


class ElasticRepositoryMixin:
    """Миксин для работы с Elasticsearch."""

    es_index_name: ClassVar[str]

    elastic: AsyncElasticsearch

    async def get_document_from_elastic(self, document_id: str) -> dict:
        try:
            doc = await self.elastic.get(index=self.es_index_name, id=str(document_id))
        except ElasticNotFoundError:
            raise NotFoundError()
        return doc["_source"]

    async def get_documents_from_elastic(self, request_body: dict | None = None, **search_options) -> list[dict]:
        if request_body is None:
            request_body = self.prepare_search_request()
        docs = await self.elastic.search(
            index=self.es_index_name,
            body=request_body,
            **search_options,
        )
        return self._prepare_documents_list(docs)

    def prepare_search_request(self, *args, **kwargs) -> dict:
        request_body = {
            "query": {"match_all": {}},
        }
        return request_body

    @staticmethod
    def _prepare_documents_list(docs: dict) -> list[dict]:
        results = [
            doc["_source"]
            for doc in docs["hits"]["hits"]
        ]
        return results


class ElasticSearchRepositoryMixin:
    """Миксин для работы с фильтрацией, пагинацией и сортировкой в Elasticsearch."""

    def prepare_search_request(
        self,
        page_size: int,
        page_number: int,
        search_query: str | None = None,
        search_fields: list[str] | None = None,
    ) -> dict:
        request_body = {
            "size": page_size,
            "from": self.calc_offset(page_size, page_number),
        }
        request_query = {"match_all": {}}
        if search_query is not None:
            request_query = {
                "multi_match": {
                    "query": search_query,
                    "fields": search_fields,
                },
            }
        request_body["query"] = request_query
        return request_body

    @staticmethod
    def calc_offset(page_size: int, page_number: int) -> int:
        """Считает offset для запроса в Elasticsearch на основе  номера страницы `page_number`."""
        if page_number <= 1:
            return 0
        offset = (page_size * page_number) - page_size
        return offset


class RedisRepositoryMixin:
    """Mixin for redis manipulations."""

    redis: Redis

    redis_cache_expire_in_seconds: ClassVar[int]

    @staticmethod
    def get_hash(url: str, length: int = 256) -> str:
        url_hash = hashlib.sha256(url.encode())
        hash_str = base64.urlsafe_b64encode(url_hash.digest()).decode("ascii")

        return hash_str[:length]

    async def get_list_of_items_from_redis(self, key, pydantic_output_class):
        items = await self.redis.get(self.get_hash(key))
        if items is None:
            return None
        return [pydantic_output_class.parse_raw(item) for item in json.loads(items)]

    async def get_item_from_redis(self, key, pydantic_output_class):
        item = await self.redis.get(str(key))
        if not item:
            return None
        return pydantic_output_class.parse_raw(item)

    async def put_item_to_redis(self, key, item_json):
        await self.redis.set(str(key), item_json, ex=self.redis_cache_expire_in_seconds)

    async def put_items_to_redis(self, items, key):
        items_json_str = json.dumps([item.json() for item in items])
        await self.redis.set(self.get_hash(key), items_json_str, ex=self.redis_cache_expire_in_seconds)
