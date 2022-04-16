from .base import BaseIdOrjsonSchema


class Genre(BaseIdOrjsonSchema):
    """Жанры фильмов."""

    name: str
