from __future__ import annotations

from typing import TYPE_CHECKING

from common.types import ApiSchema, ApiSchemaClass, Id


if TYPE_CHECKING:
    from repositories.types import Repository


class CacheServiceMixin:
    """Миксин для получения данных либо из кэша, либо из основной БД."""

    repository: Repository

    async def get_item_from_storage_or_cache(self, key: str, object_id: Id, schema_class: ApiSchemaClass) -> ApiSchema:
        """Получение объекта из основной БД или из кэша."""
        item = await self.repository.get_item_from_cache(key, schema_class)
        if item is not None:
            return item

        item = await self.repository.get_item_from_storage(object_id, schema_class)

        await self.repository.put_item_to_cache(key, item)
        return item

    async def get_items_from_storage_or_cache(self, key: str, schema_class: ApiSchemaClass) -> list[ApiSchema]:
        """Получение списка объектов из БД или из кэша."""
        items = await self.repository.get_items_from_cache(key, schema_class)
        if items is not None:
            return items

        items = await self.repository.get_all_items_from_storage(schema_class)

        await self.repository.put_items_to_cache(key, items)
        return items

    async def search_items_in_storage_or_cache(
        self, key: str, query: dict, schema_class: ApiSchemaClass, index_name: str | None = None, **options,
    ) -> list[ApiSchema]:
        """Поиск объектов по `query` в основной БД или получение из кэша."""
        if index_name is None:
            index_name = self.repository.es_index_name

        items = await self.repository.get_items_from_cache(key, schema_class)
        if items is not None:
            return items

        items = await self.repository.search_items_in_storage(schema_class, query, index_name, **options)

        await self.repository.put_items_to_cache(key, items)
        return items
