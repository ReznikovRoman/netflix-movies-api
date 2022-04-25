from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.films import FilmRepository, get_film_repository
from schemas.films import FilmDetail, FilmList


class FilmService:
    """Service for work with films."""

    def __init__(self, film_repo: FilmRepository):
        self.film_repo = film_repo

    async def get_film_by_id(self, film_id: UUID) -> FilmDetail:
        film = await self.film_repo.get_film_from_redis(film_id)
        if not film:
            film = await self.film_repo.get_film_from_elastic(film_id)
            if not film:
                return None
            await self.film_repo.put_film_to_redis(film_id, film.json())
        return film

    # async def get_all_films(
    #     self, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    # ) -> list[FilmList]:
    #     # TODO add redis cache check
    #     films = await self.film_repo.get_all_films_from_elastic(
    #         page_size=page_size,
    #         page_number=page_number,
    #         genre=genre,
    #         sort=sort,
    #     )
    #     return films

    async def get_all_films(
        self, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        string_for_hash = f"all_films{page_size}{page_number}{genre}{sort}"
        films = await self.film_repo.get_all_films_from_redis(string_for_hash)
        if not films:
            films = await self.film_repo.get_all_films_from_elastic(
                page_size=page_size,
                page_number=page_number,
                genre=genre,
                sort=sort,
            )
            if not films:
                return None
            await self.film_repo.put_all_films_to_redis(films=films, string_for_hash=string_for_hash)
        return films

    async def search_films(
        self, page_size: int, page_number: int, query: str, sort: str | None = None,
    ) -> list[FilmList]:
        string_for_hash = f"search_films{page_size}{page_number}{sort}"
        films = await self.film_repo.get_search_films_from_redis(string_for_hash)
        if not films:
            films = await self.film_repo.search_films_from_elastic(
                page_size=page_size, page_number=page_number, query=query, sort=sort,
            )
            if not films:
                return None
            await self.film_repo.put_search_films_to_redis(films=films, string_for_hash=string_for_hash)
        return films


@lru_cache()
def get_film_service(
        film_repo: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    return FilmService(film_repo)
