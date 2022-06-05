from uuid import UUID

from repositories.base import NoSQLStorageRepository
from schemas.genres import GenreDetail


class GenreRepository:
    """Репозиторий для работы с данными жанров."""

    def __init__(self, storage_repository: NoSQLStorageRepository):
        self.storage_repository = storage_repository

    async def get_by_id(self, genre_id: UUID) -> GenreDetail:
        genre = await self.storage_repository.get_by_id(str(genre_id), GenreDetail)
        return genre

    async def get_list(self) -> list[GenreDetail]:
        genres = await self.storage_repository.get_list(GenreDetail)
        return genres


def genre_key_factory(*args, **kwargs) -> str:
    genre_id: str | None = kwargs.pop("doc_id", None)
    if genre_id is not None:
        return f"genres:{genre_id}"
    return "genres:list"
