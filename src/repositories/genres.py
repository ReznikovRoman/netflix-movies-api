import json
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


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreRepository(ElasticRepositoryMixin, RedisRepositoryMixin):
    """Репозиторий для работы с данными Жанров."""

    es_index_name: ClassVar[str] = "genre"

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_from_elastic(self, genre_id: UUID) -> GenreDetail:
        genre_doc = await self.get_document_from_elastic(str(genre_id))
        return GenreDetail(**genre_doc)

    async def get_genre_from_redis(self, genre_id: UUID) -> GenreDetail:
        genre = await self.redis.get(str(genre_id))
        if not genre:
            return None
        return GenreDetail.parse_raw(genre)

    async def put_genre_to_redis(self, genre_id: UUID, genre_json_data):
        await self.redis.set(str(genre_id), genre_json_data, ex=GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def get_all_genres_from_elastic(self) -> list[GenreDetail]:
        genres_docs = await self.get_documents_from_elastic()
        return parse_obj_as(list[GenreDetail], genres_docs)

    async def get_all_genres_from_redis(self, string_for_hash) -> list[GenreDetail]:
        genres = await self.redis.get(self.get_hash(string_for_hash))
        if not genres:
            return None
        return [GenreDetail.parse_raw(genre) for genre in json.loads(genres)]

    async def put_all_genres_to_redis(self, genres, string_for_hash):
        genres_json_str = json.dumps([genre.json() for genre in genres])
        await self.redis.set(self.get_hash(string_for_hash), genres_json_str, ex=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_repository(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreRepository:
    return GenreRepository(elastic, redis)
