from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol


if TYPE_CHECKING:
    from common.types import Id, Query


class AsyncStorage(Protocol):
    """Асинхронная база данных."""

    async def get_by_id(self, instance_id: Id, *args, **kwargs) -> Any:
        """Получение записи из БД по ID `instance_id`."""

    async def search(self, query: Query, *args, **kwargs) -> Any:
        """Получение записей из БД с запросом `query`."""

    async def get_all(self, *args, **kwargs) -> Any:
        """Получение всех записей."""
