from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.films import FilmRepository
from repositories.persons import PersonRepository, get_person_repository
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail
from services.base import CacheServiceMixin


class PersonService(CacheServiceMixin):
    """Сервис для работы с персонами."""

    def __init__(self, person_repository: PersonRepository):
        self.repository = person_repository

    async def get_person_by_id(self, person_id: UUID) -> PersonShortDetail:
        key: str = f"persons:{str(person_id)}"
        return await self.get_item_from_storage_or_cache(key, person_id, PersonShortDetail)

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        key: str = f"persons:{str(person_id)}.detailed"
        return await self.get_item_from_storage_or_cache(key, person_id, PersonFullDetail)

    async def get_all_persons(
        self, request_params: str, page_size: int, page_number: int, query: str | None = None,
    ) -> list[PersonList]:
        key = await self.repository.make_key(
            request_params, min_length=self.repository.hashed_params_key_length, prefix="persons:list")
        request_body = self.repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.repository.es_person_index_search_fields,
        )
        return await self.search_items_in_storage_or_cache(key, request_body, PersonList)

    async def search_persons(
        self, request_params: str, page_size: int, page_number: int, query: str,
    ) -> list[PersonShortDetail]:
        key = await self.repository.make_key(
            request_params, min_length=self.repository.hashed_params_key_length, prefix="persons:search")
        request_body = self.repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.repository.es_person_index_search_fields,
        )
        return await self.search_items_in_storage_or_cache(key, request_body, PersonShortDetail)

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        key: str = f"persons:{str(person_id)}:films"
        request_body = self.repository.prepare_films_search_request(person_id)
        person_films = await self.search_items_in_storage_or_cache(
            key, request_body, FilmList, index_name=FilmRepository.es_index_name)
        return person_films


@lru_cache()
def get_person_service(
        person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)
