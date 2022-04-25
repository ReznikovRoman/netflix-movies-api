from functools import lru_cache
from typing import ClassVar
from uuid import UUID

import orjson
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
        person_doc = await self.get_document_from_elastic(str(person_id))
        person_films = self._get_distinct_films_from_roles(roles_data=person_doc["roles"])
        return person_films

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

    async def get_person_from_redis(self, person_id: UUID) -> PersonShortDetail | None:
        person = await self.redis.get(f"persons:{str(person_id)}")
        if not person:
            return None
        return PersonShortDetail.parse_raw(orjson.loads(person))

    async def get_person_detailed_from_redis(self, person_id: UUID) -> PersonFullDetail | None:
        person = await self.redis.get(f"persons:{str(person_id)}.detailed")
        if not person:
            return None
        return PersonFullDetail.parse_raw(orjson.loads(person))

    async def get_person_films_from_redis(self, person_id: UUID) -> list[FilmList] | None:
        person_films = await self.redis.get(f"persons:{str(person_id)}:films")
        if not person_films:
            return None
        return [FilmList.parse_raw(film) for film in orjson.loads(person_films)]

    async def get_all_persons_from_redis(self, params: str) -> list[PersonList] | None:
        hashed_params = self.calculate_hash_for_given_str(params, length=self.hashed_params_key_length)
        persons = await self.redis.get(f"persons:list:{hashed_params}")
        if not persons:
            return None
        return [PersonList.parse_raw(person) for person in orjson.loads(persons)]

    async def search_persons_in_redis(self, params: str) -> list[PersonShortDetail] | None:
        hashed_params = self.calculate_hash_for_given_str(params, length=self.hashed_params_key_length)
        persons = await self.redis.get(f"persons:search:{hashed_params}")
        if not persons:
            return None
        return [PersonShortDetail.parse_raw(person) for person in orjson.loads(persons)]

    async def put_person_to_redis(self, person_id: UUID, person: PersonShortDetail):
        serialized_person = orjson.dumps(person.json())
        await self.redis.setex(f"persons:{str(person_id)}", self.person_cache_ttl, serialized_person)

    async def put_person_detailed_to_redis(self, person_id: UUID, person: PersonFullDetail):
        serialized_person = orjson.dumps(person.json())
        await self.redis.setex(f"persons:{str(person_id)}.detailed", self.person_cache_ttl, serialized_person)

    async def put_person_films_to_redis(self, person_id: UUID, person_films: list[FilmList]) -> None:
        serialized_films = orjson.dumps([film.json() for film in person_films])
        await self.redis.setex(f"persons:{str(person_id)}:films", self.person_cache_ttl, serialized_films)

    async def put_all_persons_to_redis(self, persons: list[PersonList], params: str) -> None:
        key = await self.find_collision_free_key(
            params, min_length=self.hashed_params_key_length, prefix="persons:list")
        serialized_persons = orjson.dumps([person.json() for person in persons])
        await self.redis.setex(key, self.person_cache_ttl, serialized_persons)

    async def put_search_persons_to_redis(self, persons: list[PersonShortDetail], params: str) -> None:
        key = await self.find_collision_free_key(
            params, min_length=self.hashed_params_key_length, prefix="persons:search")
        serialized_persons = orjson.dumps([person.json() for person in persons])
        await self.redis.setex(key, self.person_cache_ttl, serialized_persons)

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
