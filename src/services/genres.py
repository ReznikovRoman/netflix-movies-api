from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from repositories.genres import GenreRepository, get_genre_repository
from schemas.genres import GenreDetail


class GenreService:
    """Service for work with genres."""

    def __init__(self, genre_repo: GenreRepository):
        self.genre_repo = genre_repo

    async def get_genre_by_id(self, genre_id: UUID) -> GenreDetail:
        genre = await self.genre_repo.get_genre_from_redis(genre_id)
        if not genre:
            genre = await self.genre_repo.get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self.genre_repo.put_genre_to_redis(genre_id, genre.json())
        return genre

    async def get_all_genres(self) -> list[GenreDetail]:
        string_for_hash = "all_genres"
        genres = await self.genre_repo.get_all_genres_from_redis(string_for_hash)
        if not genres:
            genres = await self.genre_repo.get_all_genres_from_elastic()
            if not genres:
                return None
            await self.genre_repo.put_all_genres_to_redis(genres=genres, string_for_hash=string_for_hash)
        return genres


@lru_cache()
def get_genre_service(
        genre_repo: GenreRepository = Depends(get_genre_repository),
) -> GenreService:
    return GenreService(genre_repo)
