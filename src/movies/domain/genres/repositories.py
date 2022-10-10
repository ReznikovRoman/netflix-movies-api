from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from .schemas import GenreDetail

if TYPE_CHECKING:
    from movies.infrastructure.db.repositories import NoSQLStorageRepository


class GenreRepository:
    """Genre repository."""

    def __init__(self, storage_repository: NoSQLStorageRepository) -> None:
        self.storage_repository = storage_repository

    async def get_by_id(self, genre_id: UUID, /) -> GenreDetail:
        """Get genre by id."""
        return await self.storage_repository.get_by_id(str(genre_id), schema_cls=GenreDetail)

    async def get_list(self) -> list[GenreDetail]:
        """Get genres list."""
        return await self.storage_repository.get_list(GenreDetail)


def genre_key_factory(*args, **kwargs) -> str:
    """Cache key factory."""
    genre_id: str | None = kwargs.pop("doc_id", None)
    if genre_id is not None:
        return f"genres:{genre_id}"
    return "genres:list"
