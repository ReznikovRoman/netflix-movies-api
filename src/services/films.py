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
        film_key = f"films:{str(film_id)}"
        film = await self.film_repository.get_item_from_cache(film_key, FilmDetail)
        if film is not None:
            return film

        film = await self.film_repository.get_film_from_elastic(film_id)
        await self.film_repository.put_item_to_cache(film_key, film)
        return film

    async def get_all_films(
        self, request_params: str, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        hashed_params = self.film_repository.calculate_hash_for_given_str(
            request_params, length=self.film_repository.hashed_params_key_length)
        films_key = f"films:list:{hashed_params}"
        films = await self.film_repository.get_items_from_cache(films_key, FilmList)
        if films is not None:
            return films

        films = await self.film_repository.get_all_films_from_elastic(
            page_size=page_size, page_number=page_number, genre=genre, sort=sort)

        key = await self.film_repository.make_key(
            request_params, min_length=self.film_repository.hashed_params_key_length, prefix="films:list")
        await self.film_repository.put_items_to_redis(key, films)
        return films

    async def search_films(
        self, request_params: str, page_size: int, page_number: int, query: str, sort: str | None = None,
    ) -> list[FilmList]:
        hashed_params = self.film_repository.calculate_hash_for_given_str(
            request_params, length=self.film_repository.hashed_params_key_length)
        films_key = f"films:search:{hashed_params}"
        films = await self.film_repository.get_items_from_cache(films_key, FilmList)
        if films is not None:
            return films

        films = await self.film_repository.search_films_in_elastic(
            page_size=page_size, page_number=page_number, query=query, sort=sort)

        key = await self.film_repository.make_key(
            request_params, min_length=self.film_repository.hashed_params_key_length, prefix="films:search")
        await self.film_repository.put_items_to_redis(key, films)
        return films


@lru_cache()
def get_film_service(
        film_repo: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    return FilmService(film_repo)
