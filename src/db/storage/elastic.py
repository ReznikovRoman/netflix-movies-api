from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from clients.elastic import ElasticClient

from .base import AsyncNoSQLStorage


if TYPE_CHECKING:
    from common.types import Id, Query


class ElasticStorage(AsyncNoSQLStorage):
    """БД Elasticsearch."""

    def __init__(self):
        self._class = ElasticClient

    @cached_property
    def _elastic(self) -> ElasticClient:
        return self._class()

    async def get_by_id(self, collection: str, document_id: Id, *args, **kwargs) -> dict:
        return await self._elastic.get_by_id(collection, document_id)

    async def search(self, collection: str, query: Query, *args, **kwargs) -> list[dict]:
        return await self._elastic.search(collection, query, **kwargs)

    async def get_all(self, collection: str, **options) -> list[dict]:
        query = {"query": {"match_all": {}}}
        return await self.search(collection, query, **options)
