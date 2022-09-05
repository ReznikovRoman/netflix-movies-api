from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from movies.schemas.genres import GenreDetail

if TYPE_CHECKING:
    from movies.infrastructure.db.repositories import NoSQLStorageRepository


class GenreRepository:
    """Репозиторий для работы с данными жанров."""

    def __init__(self, storage_repository: NoSQLStorageRepository) -> None:
        self.storage_repository = storage_repository

    async def get_by_id(self, genre_id: UUID) -> GenreDetail:
        """Получение жанра по ID."""
        genre = await self.storage_repository.get_by_id(str(genre_id), GenreDetail)
        return genre

    async def get_list(self) -> list[GenreDetail]:
        """Получение списка всех жанров."""
        genres = await self.storage_repository.get_list(GenreDetail)
        return genres


def genre_key_factory(*args, **kwargs) -> str:
    """Фабрика по созданию ключей жанров в кэше."""
    genre_id: str | None = kwargs.pop("doc_id", None)
    if genre_id is not None:
        return f"genres:{genre_id}"
    return "genres:list"
