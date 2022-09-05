from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from movies.common.types import Id, Query

    from .elastic import ElasticClient


class AsyncNoSQLStorage(ABC):
    """Асинхронная NoSQL база данных."""

    @abstractmethod
    async def get_by_id(self, collection: str, document_id: Id, *args, **kwargs) -> Any:
        """Получение записи из БД по ID `instance_id`."""

    @abstractmethod
    async def search(self, collection: str, query: Query, *args, **kwargs) -> Any:
        """Получение записей из БД с запросом `query`."""

    @abstractmethod
    async def get_all(self, collection: str, *args, **kwargs) -> Any:
        """Получение всех записей."""


class ElasticStorage(AsyncNoSQLStorage):
    """БД Elasticsearch."""

    def __init__(self, client: ElasticClient) -> None:
        self.client = client

    async def get_by_id(self, collection: str, document_id: Id, *args, **kwargs) -> dict:
        return await self.client.get_by_id(collection, document_id)

    async def search(self, collection: str, query: Query, *args, **kwargs) -> list[dict]:
        return await self.client.search(collection, query, **kwargs)

    async def get_all(self, collection: str, **options) -> list[dict]:
        query = {"query": {"match_all": {}}}
        return await self.search(collection, query, **options)
