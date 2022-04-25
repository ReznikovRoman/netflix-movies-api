from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.films import FilmRepository, get_film_repository
from schemas.films import FilmDetail, FilmList


class FilmService:
    """Сервис для работы с фильмами."""

    def __init__(self, film_repository: FilmRepository):
        self.film_repository = film_repository

    async def get_film_by_id(self, film_id: UUID) -> FilmDetail:
        film = await self.film_repository.get_film_from_redis(film_id)
        if film is not None:
            return film

        film = await self.film_repository.get_film_from_elastic(film_id)
        await self.film_repository.put_film_to_redis(film_id, film)
        return film

    async def get_all_films(
        self, request_params: str, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        films = await self.film_repository.get_all_films_from_redis(request_params)
        if films is not None:
            return films

        films = await self.film_repository.get_all_films_from_elastic(
            page_size=page_size, page_number=page_number, genre=genre, sort=sort)
        await self.film_repository.put_all_films_to_redis(films, params=request_params)
        return films

    async def search_films(
        self, request_params: str, page_size: int, page_number: int, query: str, sort: str | None = None,
    ) -> list[FilmList]:
        films = await self.film_repository.search_films_from_redis(request_params)
        if films is not None:
            return films

        films = await self.film_repository.search_films_from_elastic(
            page_size=page_size, page_number=page_number, query=query, sort=sort)
        await self.film_repository.put_search_films_to_redis(films, params=request_params)
        return films


@lru_cache()
def get_film_service(
        film_repo: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    return FilmService(film_repo)
