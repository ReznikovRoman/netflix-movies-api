from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aioredis
import aioredis.sentinel
from aioredis import Redis

from core.config import get_settings
from db import redis_sentinel


if TYPE_CHECKING:
    from common.types import seconds


settings = get_settings()


class RedisCacheClient:
    """Клиент Redis для кеша."""

    def __init__(self, service_name: str, connection_options: dict[str, Any]):
        self.service_name = service_name
        self.connection_options = connection_options

    async def _get_client(self, write: bool = False) -> Redis:
        if write:
            return await redis_sentinel.redis_sentinel.master_for(self.service_name, **self.connection_options)

        try:
            return await redis_sentinel.redis_sentinel.slave_for(self.service_name, **self.connection_options)
        except (aioredis.sentinel.SlaveNotFoundError, aioredis.exceptions.TimeoutError):
            return await redis_sentinel.redis_sentinel.master_for(self.service_name, **self.connection_options)

    async def get_client(self, key: str | None = None, *, write: bool = False) -> Redis:
        await self.pre_init_client()
        client = await self._get_client(write)
        await self.post_init_client(client)
        return client

    async def get(self, key: str, default: Any | None = None) -> Any:
        client = await self.get_client(key)
        value = await client.get(key)
        return default if value is None else value

    async def set(self, key: str, data: Any, *, timeout: seconds | None = None) -> bool:
        client = await self.get_client(key, write=True)
        if timeout is not None:
            return await client.set(key, data, ex=timeout)
        return await client.set(key, data)

    async def pre_init_client(self, *args, **kwargs):
        """Вызывается до начала инициализации клиента Redis."""

    async def post_init_client(self, client: Redis, *args, **kwargs) -> None:
        """Вызывается после инициализации клиента Redis."""
