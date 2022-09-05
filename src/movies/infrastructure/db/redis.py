from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

import aioredis
import aioredis.sentinel

if TYPE_CHECKING:
    from movies.common.types import seconds


async def init_redis_sentinel(sentinels: list[str], socket_timeout: float) -> AsyncIterator[aioredis.sentinel.Sentinel]:
    """Инициализация клиента Redis Sentinel."""
    sentinel_client = aioredis.sentinel.Sentinel(
        sentinels=[(sentinel, 26379) for sentinel in sentinels],
        socket_timeout=socket_timeout,
    )
    yield sentinel_client
    for sentinel in sentinel_client.sentinels:
        await sentinel.close()


class RedisClient:
    """Асинхронный клиент для работы с Redis."""

    def __init__(
        self, sentinel_client: aioredis.sentinel.Sentinel, service_name: str, connection_options: dict[str, Any],
    ) -> None:
        self.service_name = service_name
        self.connection_options = connection_options
        self.sentinel_client = sentinel_client

    async def get_client(self, key: str | None = None, *, write: bool = False) -> aioredis.Redis:
        await self.pre_init_client()
        client = await self._get_client(write=write)
        await self.post_init_client(client)
        return client

    async def get(self, key: str, /, *, default: Any | None = None) -> Any:
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

    async def post_init_client(self, client: aioredis.Redis, /, *args, **kwargs) -> None:
        """Вызывается после инициализации клиента Redis."""

    async def _get_client(self, *, write: bool = False) -> aioredis.Redis:
        if write:
            return await self.sentinel_client.master_for(self.service_name, **self.connection_options)

        try:
            slave: aioredis.Redis = await self.sentinel_client.slave_for(self.service_name, **self.connection_options)
            # XXX: в методе .slave_for() не проверяется состояние слейва (как это происходит в .discover_slaves())
            # поэтому нам приходится вручную каждый раз пинговать слейва и ловить ошибку `SlaveNotFoundError`
            await self._check_slave_health(slave)
            return slave
        except (aioredis.sentinel.SlaveNotFoundError, aioredis.exceptions.TimeoutError):
            return await self.sentinel_client.master_for(self.service_name, **self.connection_options)

    @staticmethod
    async def _check_slave_health(slave: aioredis.Redis, /) -> None:
        await slave.ping()
