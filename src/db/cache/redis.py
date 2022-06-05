from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from clients.redis_cache import RedisCacheClient

from .base import AsyncCache


if TYPE_CHECKING:
    from common.types import seconds


class RedisCache(AsyncCache):
    """Кэш с использованием Redis."""

    def __init__(self, client: RedisCacheClient, default_ttl: seconds | None = None):
        self.client = client
        self.default_ttl = default_ttl

    async def get(self, key: str, default: Any | None = None) -> Any:
        return await self.client.get(key, default)

    async def set(self, key: str, data: Any, *, ttl: seconds | None = None) -> bool:
        return await self.client.set(key, data, timeout=self.get_ttl(ttl))

    def get_ttl(self, ttl: seconds | timedelta | None = None) -> seconds | timedelta | None:
        if ttl is None and self.default_ttl is not None:
            return self.default_ttl
        if isinstance(ttl, timedelta):
            return ttl
        return None if ttl is None else max(0, int(ttl))
