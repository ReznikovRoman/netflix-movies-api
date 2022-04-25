from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.genres import GenreRepository, get_genre_repository
from schemas.genres import GenreDetail


class GenreService:
    """Сервис для работы с жанрами."""

    def __init__(self, genre_repository: GenreRepository):
        self.genre_repository = genre_repository

    async def get_genre_by_id(self, genre_id: UUID) -> GenreDetail:
        genre_key: str = f"genres:{str(genre_id)}"
        genre = await self.genre_repository.get_item_from_redis(genre_key, GenreDetail)
        if genre is not None:
            return genre

        genre = await self.genre_repository.get_genre_from_elastic(genre_id)
        await self.genre_repository.put_item_to_redis(genre_key, genre)
        return genre

    async def get_all_genres(self) -> list[GenreDetail]:
        genres_key: str = "genres:list"
        genres = await self.genre_repository.get_items_from_redis(genres_key, GenreDetail)
        if genres is not None:
            return genres

        genres = await self.genre_repository.get_all_genres_from_elastic()
        await self.genre_repository.put_items_to_redis(genres_key, genres)
        return genres


@lru_cache()
def get_genre_service(
        genre_repo: GenreRepository = Depends(get_genre_repository),
) -> GenreService:
    return GenreService(genre_repo)
