from __future__ import annotations

import base64
import hashlib
from typing import TYPE_CHECKING, ClassVar

import orjson
from elasticsearch.exceptions import NotFoundError as ElasticNotFoundError

from common.exceptions import NotFoundError
from common.types import ApiSchema, ApiSchemaClass


if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch

    from db.cache.base import AsyncCache


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

    async def get_documents_from_elastic(
        self, index_name: str | None = None, request_body: dict | None = None, **search_options,
    ) -> list[dict]:
        if request_body is None:
            request_body = self.prepare_search_request()
        if index_name is None:
            index_name = self.es_index_name

        docs = await self.elastic.search(
            index=index_name,
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


class CacheRepositoryMixin:
    """Миксин для работы с Redis."""

    cache: AsyncCache

    redis_ttl: ClassVar[int] = 5 * 60  # 5 минут

    async def get_items_from_cache(self, key: str, schema_class: ApiSchemaClass) -> list[ApiSchema] | None:
        items = await self.cache.get(key)
        if items is None:
            return None
        return [schema_class.parse_raw(item) for item in orjson.loads(items)]

    async def get_item_from_cache(self, key: str, schema_class: ApiSchemaClass) -> ApiSchema | None:
        item = await self.cache.get(key)
        if item is None:
            return None
        return schema_class.parse_raw(orjson.loads(item))

    async def put_item_to_cache(self, key: str, item: ApiSchema) -> None:
        serialized_item = orjson.dumps(item.json())
        await self.cache.set(key, serialized_item, timeout=self.redis_ttl)

    async def put_items_to_redis(self, key: str, items: list[ApiSchema]) -> None:
        serialized_items = orjson.dumps([item.json() for item in items])
        await self.cache.set(key, serialized_items, timeout=self.redis_ttl)

    async def make_key(
        self, key_to_hash: str, *, min_length: int, prefix: str | None = None, suffix: str = None,
    ) -> str:
        """Получение ключа для кеша."""
        hashed_key = self.calculate_hash_for_given_str(key_to_hash, min_length)
        key = self.make_key_with_affixes(hashed_key, prefix, suffix)
        return key

    @staticmethod
    def calculate_hash_for_given_str(given: str, length: int) -> str:
        url_hash = hashlib.sha256(given.encode())
        hash_str = base64.urlsafe_b64encode(url_hash.digest()).decode("ascii")
        return hash_str[:length]

    @staticmethod
    def make_key_with_affixes(base: str, prefix: str | None = None, suffix: str | None = None) -> str:
        key = base
        if prefix is not None:
            prefix = prefix.removesuffix(":")
            key = f"{prefix}:{key}"
        if suffix is not None:
            suffix = suffix.removeprefix(":")
            key = f"{key}:{suffix}"
        return key
