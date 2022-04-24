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
    """Репозиторий для работы с данными Персон."""

    es_index_name: ClassVar[str] = "person"

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

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        person_doc = await self.get_document_from_elastic(str(person_id))
        person_films = self._get_distinct_films_from_roles(roles_data=person_doc["roles"])
        return person_films

    async def get_all_persons(
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

    @staticmethod
    def _get_distinct_films_from_roles(roles_data: dict) -> list[FilmList]:
        """Получение уникальных фильмов из данных по ролям `roles_data`.

        Одна персона может участвовать в фильме и в качестве актера, и в качестве режиссера.
        Поэтому нужно обрабатывать данные по ролям и возвращать только уникальные фильмы.
        """
        films: list[dict] = []
        for role_data in roles_data:
            films.extend(role_data["films"])
        distinct_films: dict[str, FilmList] = {
            film["uuid"]: FilmList(**film)
            for film in films
        }
        return list(distinct_films.values())


@lru_cache()
def get_person_repository(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonRepository:
    return PersonRepository(elastic)
