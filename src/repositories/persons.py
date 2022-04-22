from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail

from .base import ElasticRepositoryMixin, ElasticSearchRepositoryMixin


class PersonRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin):
    """Репозиторий для работы с персонами."""

    es_index_name: ClassVar[str] = "persons"

    es_person_index_search_fields: ClassVar[list[str]] = [
        "full_name",
    ]

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_person_by_id(self, person_id: UUID) -> PersonShortDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonShortDetail(**person_doc)

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonFullDetail(**person_doc)

    async def get_persons(
        self, page_size: int, page_number: int, query: str | None = None, sort: str | None = None,
    ) -> list[PersonList]:
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_person_index_search_fields,
        )
        persons_docs = await self.get_documents_from_elastic(request_body=request_body, sort=sort)
        return parse_obj_as(list[PersonList], persons_docs)

    async def search_persons(self, page_size: int, page_number: int, query: str, sort: str | None = None):
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_person_index_search_fields,
        )
        persons_docs = await self.get_documents_from_elastic(request_body=request_body, sort=sort)
        return parse_obj_as(list[PersonShortDetail], persons_docs)


@lru_cache()
def get_person_repository(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonRepository:
    return PersonRepository(elastic)
