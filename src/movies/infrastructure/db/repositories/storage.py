from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from pydantic import parse_obj_as

if TYPE_CHECKING:
    from movies.common.types import ApiSchema, ApiSchemaClass

    from ..storage import AsyncNoSQLStorage
    from .cache import CacheRepository


class NoSQLStorageRepository(ABC):
    """Base repository for working with data from NOSQL storage."""

    schema_cls: ApiSchemaClass

    @abstractmethod
    async def get_by_id(self, doc_id: str, schema_cls: ApiSchemaClass) -> ApiSchema:
        """Get document by id."""

    @abstractmethod
    async def get_list(self, schema_cls: ApiSchemaClass, **search_options) -> list[ApiSchema]:
        """Get list of documents."""

    @abstractmethod
    async def search(self, query: dict, schema_cls: ApiSchemaClass, **search_options) -> list[ApiSchema]:
        """Search documents in a collection."""

    @abstractmethod
    def prepare_search_request(self, *args, **options) -> dict:
        """Prepare search request for the DB."""

    @staticmethod
    @abstractmethod
    def calc_offset(page_size: int, page_number: int) -> int:
        """Calculate offset for the DB query based on `page_size` and `page_number`."""


class ElasticRepository(NoSQLStorageRepository):
    """Repository for working with data from Elasticsearch."""

    def __init__(self, storage: AsyncNoSQLStorage, index_name: str) -> None:
        self.storage = storage
        self.index_name = index_name

    async def get_by_id(self, doc_id: str, /, *, schema_cls: ApiSchemaClass) -> ApiSchema:
        doc = await self.storage.get_by_id(doc_id, collection=self.index_name)
        return schema_cls(**doc)

    async def get_list(self, schema_cls: ApiSchemaClass, **search_options) -> list[ApiSchema]:
        docs = await self.storage.get_all(self.index_name, **search_options)
        return parse_obj_as(list[schema_cls], docs)

    async def search(self, query: dict, schema_cls: ApiSchemaClass, **search_options) -> list[ApiSchema]:
        docs = await self.storage.search(self.index_name, query, **search_options)
        return parse_obj_as(list[schema_cls], docs)

    def prepare_search_request(self, *args, **options) -> dict:
        page_size: int | None = options.pop("page_size", None)
        page_number: int | None = options.pop("page_number", None)
        search_query: str | None = options.pop("search_query", None)
        search_fields: list[str] | None = options.pop("search_fields", None)
        filter_fields: dict[str, str] | None = options.pop("filter_fields", None)

        request_body = {}
        if page_size is not None and page_number is not None:
            request_body.update({
                "size": page_size, "from": self.calc_offset(page_size, page_number),
            })
        request_query = {"match_all": {}}
        if search_query is not None:
            request_query = {
                "multi_match": {"query": search_query, "fields": search_fields},
            }
        request_body["query"] = {
            "bool": {"must": request_query},
        }
        if filter_fields:
            request_body["query"]["bool"]["filter"] = {"term": filter_fields}
        return request_body

    @staticmethod
    def calc_offset(page_size: int, page_number: int) -> int:
        if page_number <= 1:
            return 0
        offset = (page_size * page_number) - page_size
        return offset


class ElasticCacheRepository(NoSQLStorageRepository):
    """Repository for working with data from Elasticsearch and cache."""

    def __init__(
        self,
        elastic_repository: ElasticRepository,
        cache_repository: CacheRepository,
        key_factory: Callable[..., str],
    ) -> None:
        self.elastic_repository = elastic_repository
        self.cache_repository = cache_repository
        self.key_factory = key_factory

    async def get_by_id(self, doc_id: str, /, *, schema_cls: ApiSchemaClass) -> ApiSchema:
        key = self.key_factory(doc_id=doc_id, schema_cls=schema_cls)
        item = await self.cache_repository.get_item(key, schema_cls)
        if item is not None:
            return item

        item = await self.elastic_repository.get_by_id(doc_id, schema_cls=schema_cls)

        await self.cache_repository.save_item(key, item)
        return item

    async def get_list(self, schema_cls: ApiSchemaClass, **search_options) -> list[ApiSchema]:
        cache_options: dict = search_options.pop("cache_options", {})
        key = self.key_factory(**cache_options)
        items = await self.cache_repository.get_list(key, schema_cls)
        if items is not None:
            return items

        items = await self.elastic_repository.get_list(schema_cls, **search_options)

        await self.cache_repository.save_items(key, items)
        return items

    async def search(self, query: dict, schema_cls: ApiSchemaClass, **search_options) -> list[ApiSchema]:
        cache_options: dict = search_options.pop("cache_options", {})
        key = self.key_factory(**cache_options)
        items = await self.cache_repository.get_list(key, schema_cls)
        if items is not None:
            return items

        items = await self.elastic_repository.search(query, schema_cls, **search_options)

        await self.cache_repository.save_items(key, items)
        return items

    def prepare_search_request(self, *args, **options) -> dict:
        return self.elastic_repository.prepare_search_request(*args, **options)

    def calc_offset(self, page_size: int, page_number: int) -> int:
        return self.elastic_repository.calc_offset(page_size, page_number)
