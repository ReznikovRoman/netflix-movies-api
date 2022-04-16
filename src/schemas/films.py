from .base import BaseIdOrjsonSchema
from .genres import Genre
from .persons import PersonList


class MovieDetail(BaseIdOrjsonSchema):
    """Детализация фильма."""

    title: str
    imdb_rating: float
    description: str
    genre: list[Genre]
    actors: list[PersonList]
    writers: list[PersonList]
    directors: list[PersonList]


class MovieList(BaseIdOrjsonSchema):
    """Список фильмов c рейтингом."""

    title: str
    imdb_rating: float
