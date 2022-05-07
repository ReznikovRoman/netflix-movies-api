from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.genres import GenreRepository, get_genre_repository
from schemas.genres import GenreDetail
from services.base import CacheServiceMixin


class GenreService(CacheServiceMixin):
    """Сервис для работы с жанрами."""

    def __init__(self, genre_repository: GenreRepository):
        self.repository = genre_repository

    async def get_genre_by_id(self, genre_id: UUID) -> GenreDetail:
        key: str = f"genres:{str(genre_id)}"
        return await self.get_item_from_storage_or_cache(key, genre_id, GenreDetail)

    async def get_all_genres(self) -> list[GenreDetail]:
        key: str = "genres:list"
        return await self.get_items_from_storage_or_cache(key, GenreDetail)


@lru_cache()
def get_genre_service(
        genre_repo: GenreRepository = Depends(get_genre_repository),
) -> GenreService:
    return GenreService(genre_repo)
