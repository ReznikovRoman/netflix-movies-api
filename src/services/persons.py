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
        person_key: str = f"persons:{str(person_id)}"
        person = await self.person_repository.get_item_from_cache(person_key, PersonShortDetail)
        if person is not None:
            return person

        person = await self.person_repository.get_person_from_elastic(person_id)
        await self.person_repository.put_item_to_cache(person_key, person)
        return person

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        person_key: str = f"persons:{str(person_id)}.detailed"
        person = await self.person_repository.get_item_from_cache(person_key, PersonFullDetail)
        if person is not None:
            return person

        person = await self.person_repository.get_person_detailed_from_elastic(person_id)
        await self.person_repository.put_item_to_cache(person_key, person)
        return person

    async def get_all_persons(
        self, request_params: str, page_size: int, page_number: int, query: str | None = None,
    ) -> list[PersonList]:
        hashed_params = self.person_repository.calculate_hash_for_given_str(
            request_params, length=self.person_repository.hashed_params_key_length)
        persons_key: str = f"persons:list:{hashed_params}"
        persons = await self.person_repository.get_items_from_cache(persons_key, PersonList)
        if persons is not None:
            return persons

        persons = await self.person_repository.get_all_persons_from_elastic(
            page_size=page_size, page_number=page_number, query=query)

        key = await self.person_repository.make_key(
            request_params, min_length=self.person_repository.hashed_params_key_length, prefix="persons:list")
        await self.person_repository.put_items_to_redis(key, persons)
        return persons

    async def search_persons(
        self, request_params: str, page_size: int, page_number: int, query: str,
    ) -> list[PersonShortDetail]:
        hashed_params = self.person_repository.calculate_hash_for_given_str(
            request_params, length=self.person_repository.hashed_params_key_length)
        persons_key: str = f"persons:search:{hashed_params}"
        persons = await self.person_repository.get_items_from_cache(persons_key, PersonList)
        if persons is not None:
            return persons

        persons = await self.person_repository.search_persons_in_elastic(
            page_size=page_size, page_number=page_number, query=query)

        key = await self.person_repository.make_key(
            request_params, min_length=self.person_repository.hashed_params_key_length, prefix="persons:search")
        await self.person_repository.put_items_to_redis(key, persons)
        return persons

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        person_key: str = f"persons:{str(person_id)}:films"
        person_films = await self.person_repository.get_items_from_cache(person_key, FilmList)
        if person_films is not None:
            return person_films

        person_films = await self.person_repository.get_person_films_from_elastic(person_id)
        await self.person_repository.put_items_to_redis(person_key, person_films)
        return person_films


@lru_cache()
def get_person_service(
        person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)
