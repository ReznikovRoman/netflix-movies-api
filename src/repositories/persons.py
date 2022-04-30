from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from fastapi import Depends

from db.cache import AsyncCache, get_redis_cache
from db.storage import AsyncStorage, get_elastic_storage

from .base import CacheRepositoryMixin, ElasticRepositoryMixin, ElasticSearchRepositoryMixin


class PersonRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin, CacheRepositoryMixin):
    """Репозиторий для работы с данными Персон."""

    es_index_name: ClassVar[str] = "person"

    es_person_index_search_fields: ClassVar[list[str]] = [
        "full_name",
    ]

    person_cache_ttl: ClassVar[int] = 5 * 60  # 5 минут
    hashed_params_key_length: ClassVar[int] = 10

    def __init__(self, storage: AsyncStorage, cache: AsyncCache):
        self.storage = storage
        self.cache = cache

    @staticmethod
    def prepare_films_search_request(person_id: UUID) -> dict:
        query = {
            "fields": [
                "uuid",
                "title",
                "imdb_rating",
            ],
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.uuid": {"value": str(person_id)}}},
                            },
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.uuid": {"value": str(person_id)}}},
                            },
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.uuid": {"value": str(person_id)}}},
                            },
                        },
                    ],
                },
            },
        }
        return query


@lru_cache()
def get_person_repository(
        redis: AsyncCache = Depends(get_redis_cache),
        storage: AsyncStorage = Depends(get_elastic_storage),
) -> PersonRepository:
    return PersonRepository(storage, redis)
