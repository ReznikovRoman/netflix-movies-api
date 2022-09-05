import asyncio

import aioredis
import aioredis.sentinel
import backoff

from tests.functional.settings import get_settings

settings = get_settings()


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=aioredis.exceptions.RedisError,
    max_tries=5,
    max_time=2 * 60,
)
async def wait_for_redis() -> None:
    """Ожидает полноценного подключения к Redis."""
    sentinel = aioredis.sentinel.Sentinel(
        sentinels=[(sentinel, 26379) for sentinel in settings.REDIS_SENTINELS],
        socket_timeout=0.5,
    )
    master = await sentinel.master_for(
        service_name=settings.REDIS_MASTER_SET,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        password=settings.REDIS_PASSWORD,
    )
    await master.ping()


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.run_until_complete(wait_for_redis())
    loop.close()
