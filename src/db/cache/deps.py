from functools import lru_cache

from core.config import get_settings

from .redis import RedisCache


settings = get_settings()


DEFAULT_TIMEOUT = 5 * 60  # 5 минут


@lru_cache()
def get_redis_cache() -> RedisCache:
    return RedisCache(
        service_name=settings.REDIS_MASTER_SET,
        default_timeout=DEFAULT_TIMEOUT,
        params={
            "password": settings.REDIS_PASSWORD,
            "decode_responses": settings.REDIS_DECODE_RESPONSES,
        },
    )
