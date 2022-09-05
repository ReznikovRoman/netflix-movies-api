from __future__ import annotations

from typing import TYPE_CHECKING

from movies.clients.elastic import ElasticClient

from .base import AsyncNoSQLStorage

if TYPE_CHECKING:
    from movies.common.types import Id, Query


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
