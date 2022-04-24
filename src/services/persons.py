from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.persons import PersonRepository, get_person_repository
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail


class PersonService:
    """Service for work with persons."""

    def __init__(self, person_repo: PersonRepository):
        self.person_repo = person_repo

    async def get_person_by_id(self, person_id: UUID) -> PersonShortDetail:
        person = await self.person_repo.get_person_from_redis(person_id)
        if not person:
            person = await self.person_repo.get_person_from_elastic(person_id)
            if not person:
                return None
            await self.person_repo.put_person_to_redis(person_id, person.json())
        return person

    async def get_person_detail_by_id(self, person_id: UUID) -> PersonFullDetail:
        person = await self.person_repo.get_person_detail_from_redis(person_id)
        if not person:
            person = await self.person_repo.get_person_detail_from_elastic(str(person_id))
            if not person:
                return None
            await self.person_repo.put_person_detail_to_redis(person_id, person.json())
        return person

    async def get_all_persons(self, page_size: int, page_number: int, query: str | None = None) -> list[PersonList]:
        string_for_hash = f"all_persons{page_size}{page_number}{query}"
        persons = await self.person_repo.get_all_persons_from_redis(string_for_hash)
        if not persons:
            persons = await self.person_repo.get_all_persons_from_elastic(
                page_size=page_size,
                page_number=page_number,
                query=query,
            )
            if not persons:
                return None
            await self.person_repo.put_all_persons_to_redis(persons=persons, string_for_hash=string_for_hash)
        return persons

    async def search_persons(self, page_size: int, page_number: int, query: str):
        string_for_hash = f"search_persons{page_size}{page_number}{query}"
        persons = await self.person_repo.search_persons_from_redis(string_for_hash)
        if not persons:
            persons = await self.person_repo.search_persons_from_elastic(
                page_size=page_size,
                page_number=page_number,
                query=query,
            )
            if not persons:
                return None
            await self.person_repo.put_search_persons_to_redis(persons=persons, string_for_hash=string_for_hash)
        return persons

    async def get_person_films(self, person_id: UUID) -> list[FilmList]:
        string_for_hash = f"persons_film{person_id}"
        person_films = await self.person_repo.get_person_films_from_redis(string_for_hash)
        if not person_films:
            person_films = await self.person_repo.get_person_films_from_elastic(person_id)
            if not person_films:
                return None
            await self.person_repo.put_person_films_to_redis(
                person_films=person_films,
                string_for_hash=string_for_hash,
            )
        return person_films


@lru_cache()
def get_person_service(
        person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)
