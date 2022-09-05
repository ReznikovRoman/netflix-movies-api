from __future__ import annotations

from typing import TYPE_CHECKING

import orjson

if TYPE_CHECKING:
    from movies.common.types import ApiSchema, ApiSchemaClass

    from ..cache import AsyncCache


class CacheRepository:
    """Репозиторий для работы с данными из кэша."""

    def __init__(self, cache: AsyncCache, cache_ttl: int | None = 5 * 60) -> None:
        self.cache = cache
        self.cache_ttl = cache_ttl

    async def get_list(self, key: str, schema_cls: ApiSchemaClass) -> list[ApiSchema] | None:
        """Получение десериализованного списка объектов из кэша."""
        items = await self.cache.get(key)
        if items is None:
            return None
        return [schema_cls.parse_raw(item) for item in orjson.loads(items)]

    async def get_item(self, key: str, schema_cls: ApiSchemaClass) -> ApiSchema | None:
        """Получение десериализованного объекта из кэша."""
        item = await self.cache.get(key)
        if item is None:
            return None
        return schema_cls.parse_raw(orjson.loads(item))

    async def save_item(self, key: str, item: ApiSchema) -> None:
        """Сохранение объекта в кэш и его сериализация."""
        serialized_item = orjson.dumps(item.json())
        await self.cache.set(key, serialized_item, ttl=self.cache_ttl)

    async def save_items(self, key: str, items: list[ApiSchema]) -> None:
        """Сохранение списка объектов в кэш и их сериализация."""
        serialized_items = orjson.dumps([item.json() for item in items])
        await self.cache.set(key, serialized_items, ttl=self.cache_ttl)
