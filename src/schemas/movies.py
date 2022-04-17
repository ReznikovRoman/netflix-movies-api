from .base import BaseIdOrjsonSchema
from .genres import GenreDetail
from .persons import PersonList


class MovieDetail(BaseIdOrjsonSchema):
    """Фильм."""

    title: str
    imdb_rating: float
    description: str
    genre: list[GenreDetail]
    actors: list[PersonList]
    writers: list[PersonList]
    directors: list[PersonList]


class MovieList(BaseIdOrjsonSchema):
    """Список фильмов."""

    title: str
    imdb_rating: float
