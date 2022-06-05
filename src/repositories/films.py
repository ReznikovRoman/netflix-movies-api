from typing import ClassVar, Sequence
from uuid import UUID

from db.cache.base import CacheKeyBuilder
from schemas.films import FilmAccessType, FilmDetail, FilmList

from .base import NoSQLStorageRepository


class FilmRepository:
    """Репозиторий для работы с данными фильмов."""

    es_film_index_search_fields: ClassVar[Sequence[str]] = [
        "title", "description",
        "genres_names", "actors_names", "directors_names", "writers_names",
    ]
    es_film_genre_search_fields: ClassVar[Sequence[str]] = ["genres_names"]

    def __init__(self, storage_repository: NoSQLStorageRepository):
        self.storage_repository = storage_repository

    async def get_by_id(self, film_id: UUID) -> FilmDetail:
        return await self.storage_repository.get_by_id(str(film_id), FilmDetail)

    async def get_all(
        self,
        url: str,
        page_size: int, page_number: int, sort: str | None = None,
        genre: str | None = None,
        filter_fields: dict[str, str] | None = None,
    ) -> list[FilmList]:
        cache_key_prefix = self._get_film_list_key_prefix(filter_fields)
        request_options = {
            "search_query": genre, "page_size": page_size, "page_number": page_number,
            "search_fields": self.es_film_genre_search_fields, "filter_fields": filter_fields,
        }
        search_options = {
            "cache_options": {"base_key": url, "prefix": cache_key_prefix},
            "sort": sort,
        }
        search_query = self.storage_repository.prepare_search_request(**request_options)
        films = await self.storage_repository.search(search_query, FilmList, **search_options)
        return films

    async def get_public(
        self, url: str, page_size: int, page_number: int, sort: str | None = None, genre: str | None = None,
    ) -> list[FilmList]:
        films = await self.get_all(
            url, page_size, page_number, sort, genre, filter_fields={"access_type": FilmAccessType.PUBLIC.value})
        return films

    async def search(
        self, query: str, url: str, page_size: int, page_number: int, sort: str | None = None,
    ) -> list[FilmList]:
        request_options = {
            "search_query": query, "page_size": page_size, "page_number": page_number,
            "search_fields": self.es_film_index_search_fields,
        }
        search_options = {
            "cache_options": {"base_key": url, "prefix": "films:search"},
            "sort": sort,
        }
        search_query = self.storage_repository.prepare_search_request(**request_options)
        films = await self.storage_repository.search(search_query, FilmList, **search_options)
        return films

    @staticmethod
    def _get_film_list_key_prefix(filter_fields: dict | None) -> str:
        prefix = "films:list:all"
        if not filter_fields:
            return prefix
        access_type = filter_fields.get("access_type", None)
        if access_type in (FilmAccessType.PUBLIC.value,):
            return "films:list:public"
        return prefix


def film_key_factory(key_builder: CacheKeyBuilder, min_length: int, *args, **kwargs) -> str:
    film_id: str | None = kwargs.pop("doc_id", None)
    if film_id is not None:
        return f"films:{film_id}"
    base_key: str = kwargs.pop("base_key")
    prefix: str | None = kwargs.pop("prefix", None)
    suffix: str | None = kwargs.pop("suffix", None)
    return key_builder.make_key(base_key, min_length=min_length, prefix=prefix, suffix=suffix)
