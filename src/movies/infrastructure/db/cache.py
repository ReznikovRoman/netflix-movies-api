from __future__ import annotations

import base64
import datetime
import hashlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from movies.common.types import seconds

    from .redis import RedisClient


class CacheKeyBuilder:
    """Cache key builder."""

    @classmethod
    def make_key(
        cls, key_to_hash: str, *, min_length: int, prefix: str | None = None, suffix: str | None = None,
    ) -> str:
        """Create a cache key.

        Hash the given `key_to_hash` - use first `min_length` symbols from the resulting hash.
        Add prefix and suffix if necessary.
        """
        hashed_key = cls.make_hash(key_to_hash, length=min_length)
        key = cls.make_key_with_affixes(hashed_key, prefix=prefix, suffix=suffix)
        return key

    @staticmethod
    def make_hash(string: str, /, *, length: int) -> str:
        """Create `string` hash of the given length."""
        hashed_string = hashlib.sha256(string.encode())
        hash_str = base64.urlsafe_b64encode(hashed_string.digest()).decode("ascii")
        return hash_str[:length]

    @staticmethod
    def make_key_with_affixes(base: str, /, *, prefix: str | None = None, suffix: str | None = None) -> str:
        """Create a cache key with optional prefix and suffix."""
        key = base
        if prefix is not None:
            prefix = prefix.removesuffix(":")
            key = f"{prefix}:{key}"
        if suffix is not None:
            suffix = suffix.removeprefix(":")
            key = f"{key}:{suffix}"
        return key


class AsyncCache(ABC):
    """Async cache."""

    @abstractmethod
    async def get(self, key: str, /) -> Any:
        """Get data from cache by the given key."""

    @abstractmethod
    async def set(self, key: str, data: Any, *, ttl: seconds | datetime.timedelta | None = None) -> bool:
        """Save data in cache with the given key and ttl.

        Args:
            key: cache key.
            data: data for caching.
            ttl: ttl cache value.

        Returns: Has the data been saved successfully.
        """

    @abstractmethod
    def get_ttl(self, ttl: seconds | datetime.timedelta | None = None, /) -> int | None:
        """Get ttl (timeout) for cache."""


class RedisCache(AsyncCache):
    """Redis cache."""

    def __init__(self, client: RedisClient, default_ttl: seconds | datetime.timedelta | None = None) -> None:
        self.client = client
        self.default_ttl = default_ttl

    async def get(self, key: str, /, *, default: Any | None = None) -> Any:
        return await self.client.get(key, default=default)

    async def set(self, key: str, data: Any, *, ttl: seconds | None = None) -> bool:
        return await self.client.set(key, data, timeout=self.get_ttl(ttl))

    def get_ttl(self, ttl: seconds | datetime.timedelta | None = None, /) -> seconds | datetime.timedelta | None:
        if ttl is None and self.default_ttl is not None:
            return self.default_ttl
        if isinstance(ttl, datetime.timedelta):
            return ttl
        return None if ttl is None else max(0, int(ttl))
