from __future__ import annotations

from typing import TYPE_CHECKING

import orjson

if TYPE_CHECKING:
    from movies.common.types import ApiSchema, ApiSchemaClass

    from ..cache import AsyncCache


class CacheRepository:
    """Repository for working with data from cache."""

    def __init__(self, cache: AsyncCache, cache_ttl: int | None = 5 * 60) -> None:
        self.cache = cache
        self.cache_ttl = cache_ttl

    async def get_list(self, key: str, schema_cls: ApiSchemaClass) -> list[ApiSchema] | None:
        """Get deserialized list of objects from cache."""
        items = await self.cache.get(key)
        if items is None:
            return None
        return [schema_cls.parse_raw(item) for item in orjson.loads(items)]

    async def get_item(self, key: str, schema_cls: ApiSchemaClass) -> ApiSchema | None:
        """Get deserialized object from cache."""
        item = await self.cache.get(key)
        if item is None:
            return None
        return schema_cls.parse_raw(orjson.loads(item))

    async def save_item(self, key: str, item: ApiSchema) -> None:
        """Save deserialized item in cache."""
        serialized_item = orjson.dumps(item.json())
        await self.cache.set(key, serialized_item, ttl=self.cache_ttl)

    async def save_items(self, key: str, items: list[ApiSchema]) -> None:
        """Save deserialized list of items in cache."""
        serialized_items = orjson.dumps([item.json() for item in items])
        await self.cache.set(key, serialized_items, ttl=self.cache_ttl)
