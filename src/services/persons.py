from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.films import FilmRepository
from repositories.persons import PersonRepository, get_person_repository
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail


class PersonService:
    """Сервис для работы с персонами."""

    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def get_person_by_id(self, person_id: UUID) -> PersonShortDetail:
        key: str = f"persons:{str(person_id)}"
        person = await self.person_repository.get_item_from_cache(key, PersonShortDetail)
        if person is not None:
            return person

        person = await self.person_repository.get_item_from_storage(person_id, PersonShortDetail)

        await self.person_repository.put_item_to_cache(key, person)
        return person

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        key: str = f"persons:{str(person_id)}.detailed"
        person = await self.person_repository.get_item_from_cache(key, PersonFullDetail)
        if person is not None:
            return person

        person = await self.person_repository.get_item_from_storage(person_id, PersonFullDetail)

        await self.person_repository.put_item_to_cache(key, person)
        return person

    async def get_all_persons(
        self, request_params: str, page_size: int, page_number: int, query: str | None = None,
    ) -> list[PersonList]:
        key = await self.person_repository.make_key(
            request_params, min_length=self.person_repository.hashed_params_key_length, prefix="persons:list")
        persons = await self.person_repository.get_items_from_cache(key, PersonList)
        if persons is not None:
            return persons

        request_body = self.person_repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.person_repository.es_person_index_search_fields,
        )
        persons = await self.person_repository.search_items_in_storage(
            schema_class=PersonList, query=request_body)

        await self.person_repository.put_items_to_cache(key, persons)
        return persons

    async def search_persons(
        self, request_params: str, page_size: int, page_number: int, query: str,
    ) -> list[PersonShortDetail]:
        key = await self.person_repository.make_key(
            request_params, min_length=self.person_repository.hashed_params_key_length, prefix="persons:search")
        persons = await self.person_repository.get_items_from_cache(key, PersonShortDetail)
        if persons is not None:
            return persons

        request_body = self.person_repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.person_repository.es_person_index_search_fields,
        )
        persons = await self.person_repository.search_items_in_storage(
            schema_class=PersonShortDetail, query=request_body)

        await self.person_repository.put_items_to_cache(key, persons)
        return persons

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        key: str = f"persons:{str(person_id)}:films"
        person_films = await self.person_repository.get_items_from_cache(key, FilmList)
        if person_films is not None:
            return person_films

        request_body = self.person_repository.prepare_films_search_request(person_id)
        person_films = await self.person_repository.search_items_in_storage(
            schema_class=FilmList, query=request_body, index_name=FilmRepository.es_index_name)

        await self.person_repository.put_items_to_cache(key, person_films)
        return person_films


@lru_cache()
def get_person_service(
        person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)
