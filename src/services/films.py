from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.films import FilmRepository, get_film_repository
from schemas.films import FilmAccessType, FilmDetail, FilmList
from services.base import CacheServiceMixin


class FilmService(CacheServiceMixin):
    """Сервис для работы с фильмами."""

    def __init__(self, film_repository: FilmRepository):
        self.repository = film_repository

    async def get_film_by_id(self, film_id: UUID) -> FilmDetail:
        key = f"films:{str(film_id)}"
        return await self.get_item_from_storage_or_cache(key, film_id, FilmDetail)

    async def get_all_films(
        self,
        request_params: str,
        page_size: int, page_number: int,
        genre: str | None = None, sort: str | None = None, filter_fields: dict[str, str] | None = None,
    ) -> list[FilmList]:
        key = await self.repository.make_key(
            request_params, min_length=self.repository.hashed_params_key_length, prefix="films:list")
        request_body = self.repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=genre,
            search_fields=self.repository.es_film_genre_search_field,
            filter_fields=filter_fields,
        )
        return await self.search_items_in_storage_or_cache(key, request_body, FilmList, sort=sort)

    async def get_public_films(
        self, request_params: str, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        films = await self.get_all_films(
            request_params, page_size, page_number, genre, sort,
            filter_fields={"access_type": FilmAccessType.PUBLIC.value},
        )
        return films

    async def get_subscription_films(
        self, request_params: str, page_size: int, page_number: int, genre: str | None = None, sort: str | None = None,
    ) -> list[FilmList]:
        films = await self.get_all_films(
            request_params, page_size, page_number, genre, sort,
            filter_fields={"access_type": FilmAccessType.SUBSCRIPTION.value},
        )
        return films

    async def search_films(
        self, request_params: str, page_size: int, page_number: int, query: str, sort: str | None = None,
    ) -> list[FilmList]:
        key = await self.repository.make_key(
            request_params, min_length=self.repository.hashed_params_key_length, prefix="films:search")
        request_body = self.repository.prepare_search_request(
            page_size=page_size,
            page_number=page_number,
            search_query=query,
            search_fields=self.repository.es_film_index_search_fields,
        )
        return await self.search_items_in_storage_or_cache(key, request_body, FilmList, sort=sort)


@lru_cache()
def get_film_service(
        film_repo: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    return FilmService(film_repo)
