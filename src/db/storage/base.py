from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from common.types import Id, Query


class AsyncStorage(ABC):
    """Асинхронная база данных."""

    @abstractmethod
    async def get_by_id(self, instance_id: Id, *args, **kwargs) -> Any:
        """Получение записи из БД по ID `instance_id`."""

    @abstractmethod
    async def search(self, query: Query, *args, **kwargs) -> Any:
        """Получение записей из БД с запросом `query`."""

    @abstractmethod
    async def get_all(self, *args, **kwargs) -> Any:
        """Получение всех записей."""
