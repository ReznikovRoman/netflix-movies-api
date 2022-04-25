from functools import lru_cache
from typing import ClassVar
from uuid import UUID

import orjson
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

    genre_cache_ttl: ClassVar[int] = 5 * 60  # 5 минут

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_from_elastic(self, genre_id: UUID) -> GenreDetail:
        genre_doc = await self.get_document_from_elastic(str(genre_id))
        return GenreDetail(**genre_doc)

    async def get_all_genres_from_elastic(self) -> list[GenreDetail]:
        genres_docs = await self.get_documents_from_elastic()
        return parse_obj_as(list[GenreDetail], genres_docs)

    async def get_genre_from_redis(self, genre_id: UUID) -> GenreDetail | None:
        genre = await self.redis.get(f"genres:{str(genre_id)}")
        if not genre:
            return None
        return GenreDetail.parse_raw(orjson.loads(genre))

    async def get_all_genres_from_redis(self) -> list[GenreDetail] | None:
        genres = await self.redis.get("genres:list")
        if not genres:
            return None
        return [GenreDetail.parse_raw(genre_raw) for genre_raw in orjson.loads(genres)]

    async def put_genre_to_redis(self, genre_id: UUID, genre: GenreDetail) -> None:
        serialized_genre = orjson.dumps(genre.json())
        await self.redis.setex(f"genres:{str(genre_id)}", self.genre_cache_ttl, serialized_genre)

    async def put_all_genres_to_redis(self, genres: list[GenreDetail]) -> None:
        serialized_genres = orjson.dumps([genre.json() for genre in genres])
        await self.redis.setex("genres:list", self.genre_cache_ttl, serialized_genres)


@lru_cache()
def get_genre_repository(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreRepository:
    return GenreRepository(elastic, redis)
