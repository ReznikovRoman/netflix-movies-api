from .base import BaseIdOrjsonSchema


class GenreDetail(BaseIdOrjsonSchema):
    """Жанр фильма."""

    name: str
