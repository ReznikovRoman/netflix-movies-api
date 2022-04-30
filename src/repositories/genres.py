from functools import lru_cache
from typing import ClassVar

from fastapi import Depends

from db.cache import AsyncCache, get_redis_cache
from db.storage import AsyncStorage, get_elastic_storage

from .base import CacheRepositoryMixin, ElasticRepositoryMixin


class GenreRepository(ElasticRepositoryMixin, CacheRepositoryMixin):
    """Репозиторий для работы с данными Жанров."""

    es_index_name: ClassVar[str] = "genre"

    redis_ttl: ClassVar[int] = 5 * 60  # 5 минут

    def __init__(self, storage: AsyncStorage, cache: AsyncCache):
        self.storage = storage
        self.cache = cache


@lru_cache()
def get_genre_repository(
        redis: AsyncCache = Depends(get_redis_cache),
        storage: AsyncStorage = Depends(get_elastic_storage),
) -> GenreRepository:
    return GenreRepository(storage, redis)
