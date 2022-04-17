from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from schemas.films import FilmDetail, FilmList

from .base import ElasticRepositoryMixin, ElasticSearchRepositoryMixin


class FilmRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin):
    """Репозиторий для работы с фильмами."""

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

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_film_by_id(self, film_id: UUID) -> FilmDetail:
        film_doc = await self.get_document_from_elastic(str(film_id))
        return FilmDetail(**film_doc)

    async def get_all_films(
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

    async def search_films(self, page_size: int, page_number: int, query: str, sort: str | None = None):
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
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmRepository:
    return FilmRepository(elastic)
