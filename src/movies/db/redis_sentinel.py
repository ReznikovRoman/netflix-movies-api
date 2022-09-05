from aioredis.sentinel import Sentinel

redis_sentinel: Sentinel | None = None


async def get_redis_sentinel() -> Sentinel:
    return redis_sentinel
