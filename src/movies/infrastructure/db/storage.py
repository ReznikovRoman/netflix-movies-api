from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from elasticsearch.exceptions import RequestError

if TYPE_CHECKING:
    from movies.common.types import Id, Query

    from .elastic import ElasticClient


class AsyncNoSQLStorage(ABC):
    """Async NoSQL database."""

    @abstractmethod
    async def get_by_id(self, document_id: Id, /, *args, collection: str, **kwargs) -> Any:
        """Get item from DB by id."""

    @abstractmethod
    async def search(self, collection: str, query: Query, *args, **kwargs) -> Any:
        """Search items in collection by the given query."""

    @abstractmethod
    async def get_all(self, collection: str, *args, **kwargs) -> Any:
        """Get all items from collection."""


class ElasticStorage(AsyncNoSQLStorage):
    """Elasticsearch database."""

    def __init__(self, client: ElasticClient) -> None:
        self.client = client

    async def get_by_id(self, document_id: Id, /, *args, collection: str, **kwargs) -> dict:
        return await self.client.get_by_id(document_id, index=collection)

    async def search(self, collection: str, query: Query, *args, **kwargs) -> list[dict]:
        try:
            return await self.client.search(collection, query, **kwargs)
        except RequestError:
            return []

    async def get_all(self, collection: str, **options) -> list[dict]:
        query = {"query": {"match_all": {}}}
        return await self.search(collection, query, **options)
