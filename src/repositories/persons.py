from functools import lru_cache
from typing import ClassVar
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import parse_obj_as

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail

from .base import ElasticRepositoryMixin, ElasticSearchRepositoryMixin, RedisRepositoryMixin
from .films import FilmRepository


class PersonRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin, RedisRepositoryMixin):
    """Репозиторий для работы с данными Персон."""

    es_index_name: ClassVar[str] = "person"

    es_person_index_search_fields: ClassVar[list[str]] = [
        "full_name",
    ]

    person_cache_ttl: ClassVar[int] = 5 * 60  # 5 минут
    hashed_params_key_length: ClassVar[int] = 10

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_person_from_elastic(self, person_id: UUID) -> PersonShortDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonShortDetail(**person_doc)

    async def get_person_detailed_from_elastic(self, person_id: UUID) -> PersonFullDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonFullDetail(**person_doc)

    async def get_person_films_from_elastic(self, person_id: UUID) -> list[FilmList]:
        query = {
            "fields": [
                "uuid",
                "title",
                "imdb_rating",
            ],
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.uuid": {"value": str(person_id)}}},
                            },
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.uuid": {"value": str(person_id)}}},
                            },
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.uuid": {"value": str(person_id)}}},
                            },
                        },
                    ],
                },
            },
        }
        films_docs = await self.get_documents_from_elastic(index_name=FilmRepository.es_index_name, request_body=query)
        return parse_obj_as(list[FilmList], films_docs)

    async def get_all_persons_from_elastic(
        self, page_size: int, page_number: int, query: str | None = None,
    ) -> list[PersonList]:
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_person_index_search_fields,
        )
        persons_docs = await self.get_documents_from_elastic(request_body=request_body)
        return parse_obj_as(list[PersonList], persons_docs)

    async def search_persons_in_elastic(self, page_size: int, page_number: int, query: str) -> list[PersonShortDetail]:
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_person_index_search_fields,
        )
        persons_docs = await self.get_documents_from_elastic(request_body=request_body)
        return parse_obj_as(list[PersonShortDetail], persons_docs)


@lru_cache()
def get_person_repository(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonRepository:
    return PersonRepository(elastic, redis)
