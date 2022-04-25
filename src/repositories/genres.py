from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from schemas.genres import GenreDetail

from .base import ElasticRepositoryMixin, RedisRepositoryMixin


class GenreRepository(ElasticRepositoryMixin, RedisRepositoryMixin):
    """Репозиторий для работы с данными Жанров."""

    es_index_name: ClassVar[str] = "genre"

    redis_ttl: ClassVar[int] = 5 * 60  # 5 минут

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_from_elastic(self, genre_id: UUID) -> GenreDetail:
        genre_doc = await self.get_document_from_elastic(str(genre_id))
        return GenreDetail(**genre_doc)

    async def get_all_genres_from_elastic(self) -> list[GenreDetail]:
        genres_docs = await self.get_documents_from_elastic()
        return parse_obj_as(list[GenreDetail], genres_docs)


@lru_cache()
def get_genre_repository(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreRepository:
    return GenreRepository(elastic, redis)
