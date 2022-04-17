from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from schemas.genres import GenreDetail

from .base import ElasticRepositoryMixin


class GenreRepository(ElasticRepositoryMixin):
    """Репозиторий для работы с данными Жанров."""

    es_index_name: ClassVar[str] = "genre"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_genre_by_id(self, genre_id: UUID) -> GenreDetail:
        genre_doc = await self.get_document_from_elastic(str(genre_id))
        return GenreDetail(**genre_doc)

    async def get_all_genres(self) -> list[GenreDetail]:
        genres_docs = await self.get_documents_from_elastic()
        return parse_obj_as(list[GenreDetail], genres_docs)


@lru_cache()
def get_genre_repository(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreRepository:
    return GenreRepository(elastic)
