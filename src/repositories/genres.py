from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.cache import AsyncCache, get_redis_cache
from db.elastic import get_elastic
from schemas.genres import GenreDetail

from .base import CacheRepositoryMixin, ElasticRepositoryMixin


class GenreRepository(ElasticRepositoryMixin, CacheRepositoryMixin):
    """Репозиторий для работы с данными Жанров."""

    es_index_name: ClassVar[str] = "genre"

    redis_ttl: ClassVar[int] = 5 * 60  # 5 минут

    def __init__(self, elastic: AsyncElasticsearch, cache: AsyncCache):
        self.elastic = elastic
        self.cache = cache

    async def get_genre_from_elastic(self, genre_id: UUID) -> GenreDetail:
        genre_doc = await self.get_document_from_elastic(str(genre_id))
        return GenreDetail(**genre_doc)

    async def get_all_genres_from_elastic(self) -> list[GenreDetail]:
        genres_docs = await self.get_documents_from_elastic()
        return parse_obj_as(list[GenreDetail], genres_docs)


@lru_cache()
def get_genre_repository(
        redis: AsyncCache = Depends(get_redis_cache),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreRepository:
    return GenreRepository(elastic, redis)
