from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from common.types import Id, Query


class AsyncNoSQLStorage(ABC):
    """Асинхронная NoSQL база данных."""

    @abstractmethod
    async def get_by_id(self, collection: str, document_id: Id, *args, **kwargs) -> Any:
        """Получение записи из БД по ID `instance_id`."""
        raise NotImplementedError

    @abstractmethod
    async def search(self, collection: str, query: Query, *args, **kwargs) -> Any:
        """Получение записей из БД с запросом `query`."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, collection: str, *args, **kwargs) -> Any:
        """Получение всех записей."""
        raise NotImplementedError
