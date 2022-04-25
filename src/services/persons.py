from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.persons import PersonRepository, get_person_repository
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail


class PersonService:
    """Сервис для работы с персонами."""

    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    async def get_person_by_id(self, person_id: UUID) -> PersonShortDetail:
        person = await self.person_repository.get_person_from_redis(person_id)
        if person is not None:
            return person

        person = await self.person_repository.get_person_from_elastic(person_id)
        await self.person_repository.put_person_to_redis(person_id, person)
        return person

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        person = await self.person_repository.get_person_detailed_from_redis(person_id)
        if person is not None:
            return person

        person = await self.person_repository.get_person_detailed_from_elastic(person_id)
        await self.person_repository.put_person_detailed_to_redis(person_id, person)
        return person

    async def get_all_persons(
        self, request_params: str, page_size: int, page_number: int, query: str | None = None,
    ) -> list[PersonList]:
        persons = await self.person_repository.get_all_persons_from_redis(request_params)
        if persons is not None:
            return persons

        persons = await self.person_repository.get_all_persons_from_elastic(
            page_size=page_size, page_number=page_number, query=query)
        await self.person_repository.put_all_persons_to_redis(persons, params=request_params)
        return persons

    async def search_persons(self, request_params: str, page_size: int, page_number: int, query: str):
        persons = await self.person_repository.search_persons_in_redis(request_params)
        if persons is not None:
            return persons

        persons = await self.person_repository.search_persons_in_elastic(
            page_size=page_size, page_number=page_number, query=query)
        await self.person_repository.put_search_persons_to_redis(persons, params=request_params)
        return persons

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        person_films = await self.person_repository.get_person_films_from_redis(person_id)
        if person_films is not None:
            return person_films

        person_films = await self.person_repository.get_person_films_from_elastic(person_id)
        await self.person_repository.put_person_films_to_redis(person_id, person_films)
        return person_films


@lru_cache()
def get_person_service(
        person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)
