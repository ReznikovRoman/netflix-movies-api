from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from schemas.films import FilmDetail, FilmList

from .base import ElasticRepositoryMixin, ElasticSearchRepositoryMixin


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin):
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

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_film_from_elastic(self, film_id: UUID) -> FilmDetail:
        film_doc = await self.get_document_from_elastic(str(film_id))
        return FilmDetail(**film_doc)

    async def get_film_from_redis(self, film_id: UUID) -> FilmDetail:
        data = await self.redis.get(str(film_id))
        if not data:
            return None
        return FilmDetail.parse_raw(data)

    async def put_film_to_redis(self, film_id: UUID, film_json_data):
        await self.redis.set(str(film_id), film_json_data, ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_all_films_from_elastic(
        self, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=genre,
            search_fields=self.es_film_genre_search_field,
        )
        films_docs = await self.get_documents_from_elastic(request_body=request_body, sort=sort)
        return parse_obj_as(list[FilmList], films_docs)

    async def search_films_from_elastic(
        self, page_size: int, page_number: int, query: str, sort: str | None = None,
    ) -> list[FilmList]:
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_film_index_search_fields,
        )
        films_docs = await self.get_documents_from_elastic(request_body=request_body, sort=sort)
        return parse_obj_as(list[FilmList], films_docs)


@lru_cache()
def get_film_repository(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmRepository:
    return FilmRepository(elastic, redis)
