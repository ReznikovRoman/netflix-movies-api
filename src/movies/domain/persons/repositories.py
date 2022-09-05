from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Sequence
from uuid import UUID

from .schemas import PersonList, PersonShortDetail

if TYPE_CHECKING:
    from movies.common.types import ApiSchemaClass
    from movies.domain.films import FilmList, FilmRepository
    from movies.domain.roles.schemas import PersonFullDetail
    from movies.infrastructure.db.cache import CacheKeyBuilder
    from movies.infrastructure.db.repositories import NoSQLStorageRepository


class PersonRepository:
    """Репозиторий для работы с данными персон."""

    es_person_index_search_fields: ClassVar[Sequence[str]] = ["full_name"]

    def __init__(self, storage_repository: NoSQLStorageRepository, film_repository: FilmRepository) -> None:
        self.storage_repository = storage_repository
        self.film_repository = film_repository

    async def get_by_id(self, person_id: UUID) -> PersonShortDetail:
        """Получение персоны по ID."""
        return await self.storage_repository.get_by_id(str(person_id), PersonShortDetail)

    async def get_by_id_detailed(self, person_id: UUID) -> PersonFullDetail:
        """Получение полной информации о персоне по ID."""
        from movies.domain.roles.schemas import PersonFullDetail

        return await self.storage_repository.get_by_id(str(person_id), PersonFullDetail)

    async def get_all(self, url: str, page_size: int, page_number: int) -> list[PersonList]:
        """Получение списка всех персон."""
        search_options = {
            "cache_options": {"base_key": url, "prefix": "persons:list"},
        }
        request_body = self.storage_repository.prepare_search_request(page_size=page_size, page_number=page_number)
        return await self.storage_repository.search(request_body, PersonList, **search_options)

    async def search(self, query: str, url: str, page_size: int, page_number: int) -> list[PersonShortDetail]:
        """Поиск по персонам."""
        request_options = {
            "search_query": query, "page_size": page_size, "page_number": page_number,
            "search_fields": self.es_person_index_search_fields,
        }
        search_options = {
            "cache_options": {"base_key": url, "prefix": "persons:search"},
        }
        search_query = self.storage_repository.prepare_search_request(**request_options)
        return await self.storage_repository.search(search_query, PersonShortDetail, **search_options)

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        """Получение фильмов с участием персоны `person_id`."""
        from movies.domain.films.schemas import FilmList

        person_id = str(person_id)
        search_options = {
            "cache_options": {"base_key": person_id, "prefix": "persons", "suffix": "films"},
        }
        search_query = self.prepare_films_search_request(person_id)
        return await self.film_repository.storage_repository.search(
            search_query, FilmList, **search_options)

    @staticmethod
    def prepare_films_search_request(person_id: str) -> dict:
        """Запрос в Elasticsearch на получение фильмов персоны."""
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
    """Фабрика по созданию ключей персон в кэше."""
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
