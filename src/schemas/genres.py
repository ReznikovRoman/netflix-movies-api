from uuid import UUID, uuid4

from .base import BaseIdOrjsonSchema


class Genre(BaseIdOrjsonSchema):
    """Жанры фильмов."""

    name: str
