from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from clients.elastic import ElasticClient


if TYPE_CHECKING:
    from common.types import Id, Query


class ElasticStorage:
    """БД Elasticsearch."""

    def __init__(self):
        self._class = ElasticClient

    @cached_property
    def _elastic(self):
        return self._class()

    async def get_by_id(self, instance_id: Id, index: str) -> dict:
        return await self._elastic.get_by_id(instance_id, index)

    async def search(self, query: Query, index: str, **options) -> list[dict]:
        return await self._elastic.search(query, index, **options)

    async def get_all(self, index: str, **options) -> list[dict]:
        query = {
            "query": {"match_all": {}},
        }
        return await self.search(query, index, **options)
