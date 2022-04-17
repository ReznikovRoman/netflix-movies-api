from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError as ElasticNotFoundError

from fastapi import Depends

from common.exceptions import NotFoundError
from db.elastic import get_elastic
from schemas.films import FilmDetail


class FilmRepository:
    """Репозиторий для работы с фильмами."""

    es_index_name: ClassVar[str] = "movies"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_film_by_id(self, film_id: UUID) -> FilmDetail:
        film = await self._get_film_from_elastic(film_id)
        return film

    async def _get_film_from_elastic(self, film_id: UUID) -> FilmDetail:
        try:
            doc = await self.elastic.get(index=self.es_index_name, id=str(film_id))
        except ElasticNotFoundError:
            raise NotFoundError()
        return FilmDetail(**doc["_source"])


@lru_cache()
def get_film_repository(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmRepository:
    return FilmRepository(elastic)
