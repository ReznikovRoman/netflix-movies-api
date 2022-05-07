from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from clients.redis_cache import RedisCacheClient

from .base import AsyncCache


if TYPE_CHECKING:
    from common.types import seconds


class RedisCache(AsyncCache):
    """Кеш с использованием Redis в качестве бекенда."""

    def __init__(self, service_name: str, params: dict[str, Any] = None, default_timeout: seconds | None = None):
        self.default_timeout = default_timeout
        self.service_name = service_name

        self.params = {}
        if params is not None:
            self.params = params

        self._class = RedisCacheClient

    @cached_property
    def _cache(self):
        return self._class(service_name=self.service_name, connection_options=self.params)

    async def get(self, key: str, default: Any | None = None) -> Any:
        return await self._cache.get(key, default)

    async def set(self, key: str, data: Any, *, timeout: seconds | None = None) -> bool:
        return await self._cache.set(key, data, timeout=self.get_timeout(timeout))

    def get_timeout(self, timeout: seconds | None = None) -> int | None:
        if self.default_timeout is not None:
            timeout = self.default_timeout
        return None if timeout is None else max(0, int(timeout))
