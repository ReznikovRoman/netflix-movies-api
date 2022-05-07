from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from common.types import seconds


class AsyncCache(ABC):
    """Асинхронный кеш."""

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Получение данных из кеша по ключу `key`."""

    @abstractmethod
    async def set(self, key: str, data: Any, *, timeout: seconds | None = None) -> bool:
        """Сохранение данных с заданным ttl и ключом.

        Args:
            key (str): ключ, по которому надо сохранять данные.
            data (Any): данные для сохранения.
            timeout (int): значение ttl (время жизни), в секундах.

        Returns:
            bool: были ли данные сохранены успешно.
        """

    @abstractmethod
    def get_timeout(self, timeout: seconds | None = None) -> int | None:
        """Получение `ttl` (таймаута) для записи в кеше."""
