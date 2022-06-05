from typing import ClassVar, Sequence
from uuid import UUID

from common.types import ApiSchemaClass
from db.cache.base import CacheKeyBuilder
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail

from .base import NoSQLStorageRepository
from .films import FilmRepository


class PersonRepository:
    """Репозиторий для работы с данными персон."""

    es_person_index_search_fields: ClassVar[Sequence[str]] = ["full_name"]

    def __init__(self, storage_repository: NoSQLStorageRepository, film_repository: FilmRepository):
        self.storage_repository = storage_repository
        self.film_repository = film_repository

    async def get_by_id(self, person_id: UUID) -> PersonShortDetail:
        person = await self.storage_repository.get_by_id(str(person_id), PersonShortDetail)
        return person

    async def get_by_id_detailed(self, person_id: UUID) -> PersonFullDetail:
        person = await self.storage_repository.get_by_id(str(person_id), PersonFullDetail)
        return person

    async def get_all(self, url: str, page_size: int, page_number: int) -> list[PersonList]:
        search_options = {
            "cache_options": {"base_key": url, "prefix": "persons:list"},
        }
        request_body = self.storage_repository.prepare_search_request(page_size=page_size, page_number=page_number)
        persons = await self.storage_repository.search(request_body, PersonList, **search_options)
        return persons

    async def search(self, query: str, url: str, page_size: int, page_number: int) -> list[PersonShortDetail]:
        request_options = {
            "search_query": query, "page_size": page_size, "page_number": page_number,
            "search_fields": self.es_person_index_search_fields,
        }
        search_options = {
            "cache_options": {"base_key": url, "prefix": "persons:search"},
        }
        search_query = self.storage_repository.prepare_search_request(**request_options)
        persons = await self.storage_repository.search(search_query, PersonShortDetail, **search_options)
        return persons

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        person_id = str(person_id)
        search_options = {
            "cache_options": {"base_key": person_id, "prefix": "persons", "suffix": "films"},
        }
        search_query = self.prepare_films_search_request(person_id)
        person_films = await self.film_repository.storage_repository.search(search_query, FilmList, **search_options)
        return person_films

    @staticmethod
    def prepare_films_search_request(person_id: str) -> dict:
        query = {
            "fields": [
                "uuid",
                "title",
                "imdb_rating",
                "access_type",
            ],
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.uuid": {"value": person_id}}},
                            },
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.uuid": {"value": person_id}}},
                            },
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.uuid": {"value": person_id}}},
                            },
                        },
                    ],
                },
            },
        }
        return query


def person_key_factory(key_builder: CacheKeyBuilder, min_length: int, *args, **kwargs) -> str:
    person_id: str | None = kwargs.pop("doc_id", None)
    schema_cls: ApiSchemaClass | None = kwargs.pop("schema_cls", None)
    if person_id is not None:
        if schema_cls is PersonShortDetail:
            return f"persons:{person_id}"
        return f"persons:{person_id}.detailed"
    base_key: str = kwargs.pop("base_key")
    prefix: str | None = kwargs.pop("prefix", None)
    suffix: str | None = kwargs.pop("suffix", None)
    return key_builder.make_key(base_key, min_length=min_length, prefix=prefix, suffix=suffix)
