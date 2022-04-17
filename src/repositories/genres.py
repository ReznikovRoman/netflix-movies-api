from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError as ElasticNotFoundError
from pydantic import parse_obj_as

from fastapi import Depends

from common.exceptions import NotFoundError
from db.elastic import get_elastic
from schemas.genres import GenreDetail


class GenreRepository:
    """Репозиторий для работы с данными Жанров."""

    es_index_name: ClassVar[str] = "genre"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_genre_by_id(self, genre_id: UUID) -> GenreDetail:
        genre = await self._get_genre_from_elastic(genre_id)
        return genre

    async def get_all_genres(self) -> list[GenreDetail]:
        genres = await self._get_genres_from_elastic()
        return genres

    async def _get_genre_from_elastic(self, genre_id: UUID) -> GenreDetail:
        try:
            doc = await self.elastic.get(index=self.es_index_name, id=str(genre_id))
        except ElasticNotFoundError:
            raise NotFoundError()
        return GenreDetail(**doc["_source"])

    async def _get_genres_from_elastic(self) -> list[GenreDetail]:
        request_body = {
            "query": {"match_all": {}},
        }
        docs = await self.elastic.search(index=self.es_index_name, body=request_body)
        results = [
            result["_source"]
            for result in docs["hits"]["hits"]
        ]
        genres = parse_obj_as(list[GenreDetail], results)
        return genres


@lru_cache()
def get_genre_repository(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreRepository:
    return GenreRepository(elastic)
