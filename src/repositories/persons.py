import json
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


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonRepository(ElasticSearchRepositoryMixin, ElasticRepositoryMixin, RedisRepositoryMixin):
    """Репозиторий для работы с данными Персон."""

    es_index_name: ClassVar[str] = "person"

    es_person_index_search_fields: ClassVar[list[str]] = [
        "full_name",
    ]

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis):
        self.elastic = elastic
        self.redis = redis

    async def get_person_from_elastic(self, person_id: UUID) -> PersonShortDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonShortDetail(**person_doc)

    async def get_person_from_redis(self, person_id: UUID) -> PersonShortDetail:
        data = await self.redis.get(str(person_id))
        if not data:
            return None
        return PersonShortDetail.parse_raw(data)

    async def put_person_to_redis(self, person_id: UUID, person_json_data):
        await self.redis.set(str(person_id), person_json_data, ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def get_person_detail_from_elastic(self, person_id: UUID) -> PersonFullDetail:
        person_doc = await self.get_document_from_elastic(str(person_id))
        return PersonFullDetail(**person_doc)

    async def get_person_detail_from_redis(self, person_id: UUID) -> PersonFullDetail:
        data = await self.redis.get(str(person_id))
        if not data:
            return None
        return PersonFullDetail.parse_raw(data)

    async def put_person_detail_to_redis(self, person_id: UUID, person_json_data):
        await self.redis.set(str(person_id), person_json_data, ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def get_person_films_from_elastic(self, person_id: UUID) -> list[FilmList]:
        person_doc = await self.get_document_from_elastic(str(person_id))
        person_films = self._get_distinct_films_from_roles(roles_data=person_doc["roles"])
        return person_films

    async def get_person_films_from_redis(self, string_for_hash):
        data = await self.redis.get(self.get_hash(string_for_hash))
        if not data:
            return None
        return [FilmList.parse_raw(film) for film in json.loads(data)]

    async def put_person_films_to_redis(self, string_for_hash, person_films):
        json_str = json.dumps([film.json() for film in person_films])
        await self.redis.set(self.get_hash(string_for_hash), json_str, ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def get_all_persons_from_elastic(
        self, page_size: int,
        page_number: int, query: str | None = None,
    ) -> list[PersonList]:
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_person_index_search_fields,
        )
        persons_docs = await self.get_documents_from_elastic(request_body=request_body)
        return parse_obj_as(list[PersonList], persons_docs)

    async def get_all_persons_from_redis(self, string_for_hash):
        data = await self.redis.get(self.get_hash(string_for_hash))
        if not data:
            return None
        return [PersonList.parse_raw(person) for person in json.loads(data)]

    async def put_all_persons_to_redis(self, string_for_hash, persons):
        json_str = json.dumps([person.json() for person in persons])
        await self.redis.set(self.get_hash(string_for_hash), json_str, ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def search_persons_from_elastic(self, page_size: int, page_number: int, query: str):
        request_body = self.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.es_person_index_search_fields,
        )
        persons_docs = await self.get_documents_from_elastic(request_body=request_body)
        return parse_obj_as(list[PersonShortDetail], persons_docs)

    async def search_persons_from_redis(self, string_for_hash):
        data = await self.redis.get(self.get_hash(string_for_hash))
        if not data:
            return None
        return [PersonShortDetail.parse_raw(person) for person in json.loads(data)]

    async def put_search_persons_to_redis(self, string_for_hash, persons):
        json_str = json.dumps([person.json() for person in persons])
        await self.redis.set(self.get_hash(string_for_hash), json_str, ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

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
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonRepository:
    return PersonRepository(elastic, redis)
