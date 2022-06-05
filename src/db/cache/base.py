from __future__ import annotations

import base64
import hashlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import orjson


if TYPE_CHECKING:
    from common.types import ApiSchema, ApiSchemaClass, seconds


class AsyncCache(ABC):
    """Асинхронный кэш."""

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Получение данных из кэша по ключу `key`."""

    @abstractmethod
    async def set(self, key: str, data: Any, *, ttl: seconds | None = None) -> bool:
        """Сохранение данных с заданным ttl и ключом.

        Args:
            key (str): ключ, по которому надо сохранять данные.
            data (Any): данные для сохранения.
            ttl (int): значение ttl (время жизни), в секундах.

        Returns:
            bool: были ли данные сохранены успешно.
        """

    @abstractmethod
    def get_ttl(self, ttl: seconds | None = None) -> int | None:
        """Получение `ttl` (таймаута) для записи в кэше."""


class CacheKeyBuilder:
    """Генератор ключей для кэша."""

    @classmethod
    def make_key(
        cls, key_to_hash: str, *, min_length: int, prefix: str | None = None, suffix: str | None = None,
    ) -> str:
        """Получение ключа для кэша.

        Хэшируем исходной ключ `key_to_hash` - используем первые `min_length` символов из полученного хеша.
        При необходимости добавляем префикс и суффикс.
        """
        hashed_key = cls.calculate_hash_for_given_str(key_to_hash, min_length)
        key = cls.make_key_with_affixes(hashed_key, prefix, suffix)
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


class CacheRepository:
    """Репозиторий для работы с данными из кэша."""

    def __init__(self, cache: AsyncCache, cache_ttl: int | None = 5 * 60):
        self.cache = cache
        self.cache_ttl = cache_ttl

    async def get_list(self, key: str, schema_cls: ApiSchemaClass) -> list[ApiSchema] | None:
        items = await self.cache.get(key)
        if items is None:
            return None
        return [schema_cls.parse_raw(item) for item in orjson.loads(items)]

    async def get_item(self, key: str, schema_cls: ApiSchemaClass) -> ApiSchema | None:
        item = await self.cache.get(key)
        if item is None:
            return None
        return schema_cls.parse_raw(orjson.loads(item))

    async def save_item(self, key: str, item: ApiSchema) -> None:
        serialized_item = orjson.dumps(item.json())
        await self.cache.set(key, serialized_item, ttl=self.cache_ttl)

    async def save_items(self, key: str, items: list[ApiSchema]) -> None:
        serialized_items = orjson.dumps([item.json() for item in items])
        await self.cache.set(key, serialized_items, ttl=self.cache_ttl)
