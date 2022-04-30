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
        key = f"films:{str(film_id)}"
        film = await self.film_repository.get_item_from_cache(key, FilmDetail)
        if film is not None:
            return film

        film = await self.film_repository.get_item_from_storage(film_id, FilmDetail)

        await self.film_repository.put_item_to_cache(key, film)
        return film

    async def get_all_films(
        self, request_params: str, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        key = await self.film_repository.make_key(
            request_params, min_length=self.film_repository.hashed_params_key_length, prefix="films:list")
        films = await self.film_repository.get_items_from_cache(key, FilmList)
        if films is not None:
            return films

        request_body = self.film_repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=genre,
            search_fields=self.film_repository.es_film_genre_search_field,
        )
        films = await self.film_repository.search_items_in_storage(
            schema_class=FilmList, query=request_body, sort=sort)

        await self.film_repository.put_items_to_cache(key, films)
        return films

    async def search_films(
        self, request_params: str, page_size: int, page_number: int, query: str, sort: str | None = None,
    ) -> list[FilmList]:
        key = await self.film_repository.make_key(
            request_params, min_length=self.film_repository.hashed_params_key_length, prefix="films:search")
        films = await self.film_repository.get_items_from_cache(key, FilmList)
        if films is not None:
            return films

        request_body = self.film_repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.film_repository.es_film_index_search_fields,
        )
        films = await self.film_repository.search_items_in_storage(
            schema_class=FilmList, query=request_body, sort=sort)

        await self.film_repository.put_items_to_cache(key, films)
        return films


@lru_cache()
def get_film_service(
        film_repo: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    return FilmService(film_repo)
