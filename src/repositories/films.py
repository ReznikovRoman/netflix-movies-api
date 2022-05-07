from functools import lru_cache
from typing import ClassVar

from fastapi import Depends

from db.cache import AsyncCache, get_redis_cache
from db.storage import AsyncNoSQLStorage, get_elastic_storage

from .base import CacheRepositoryMixin, ElasticRepositoryMixin, ElasticSearchRepositoryMixin


class FilmRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin, CacheRepositoryMixin):
    """Репозиторий для работы с данными Фильмов."""

    es_index_name: ClassVar[str] = "movies"

    es_film_index_search_fields: ClassVar[list[str]] = [
        "title",
        "description",
        "genres_names",
        "actors_names",
        "directors_names",
        "writers_names",
    ]
    es_film_genre_search_field: ClassVar[list[str]] = ["genres_names"]

    film_cache_ttl: ClassVar[int] = 5 * 60  # 5 минут
    hashed_params_key_length: ClassVar[int] = 10

    def __init__(self, storage: AsyncNoSQLStorage, cache: AsyncCache):
        self.storage = storage
        self.cache = cache


@lru_cache()
def get_film_repository(
        cache: AsyncCache = Depends(get_redis_cache),
        storage: AsyncNoSQLStorage = Depends(get_elastic_storage),
) -> FilmRepository:
    return FilmRepository(storage, cache)
