from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail

from .base import ElasticRepositoryMixin, ElasticSearchRepositoryMixin


class PersonRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin):
    """Репозиторий для работы с персонами."""

    es_index_name: ClassVar[str] = "person"

    es_person_index_search_fields: ClassVar[list[str]] = [
        "full_name",
    ]

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @staticmethod
    def _format_films_list(films_ids):
        """Format string of films_ids from elastic."""
        return films_ids.replace("{", "").replace("}", "").split(",")

    @staticmethod
    def _get_distinct_film_list(roles_data):
        film_list = []
        for role in roles_data:
            film_list.extend(role["films"])
        film_list_distinct = list({v["uuid"]: v for v in film_list}.values())
        return film_list_distinct

    async def get_person_by_id(self, person_id: UUID) -> PersonShortDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        person_doc["films_ids"] = self._format_films_list(person_doc["films_ids"])
        return PersonShortDetail(**person_doc)

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonFullDetail(**person_doc)

    async def get_films_of_person(self, person_id: UUID) -> list[FilmList]:
        person_data = await self.get_document_from_elastic(str(person_id))
        film_list_distinct = self._get_distinct_film_list(person_data["roles"])
        return parse_obj_as(list[FilmList], film_list_distinct)

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
