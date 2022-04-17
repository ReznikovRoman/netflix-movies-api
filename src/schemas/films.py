from .base import BaseIdOrjsonSchema
from .genres import GenreDetail
from .persons import PersonList


class FilmDetail(BaseIdOrjsonSchema):
    """Фильм."""

    title: str
    imdb_rating: float | None
    description: str
    genre: list[GenreDetail]
    actors: list[PersonList]
    writers: list[PersonList]
    directors: list[PersonList]


class FilmList(BaseIdOrjsonSchema):
    """Список фильмов."""

    title: str
    imdb_rating: float | None
