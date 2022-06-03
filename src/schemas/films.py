import datetime
from enum import Enum

from .base import BaseIdOrjsonSchema
from .genres import GenreDetail
from .persons import PersonList


class FilmAgeRating(str, Enum):
    """Возрастной рейтинг фильма.

    Список возрастных рейтингов: https://bit.ly/3xuSpB0.
    """

    GENERAL = "G"
    PARENTAL_GUIDANCE = "PG"
    PARENTS = "PG-13"
    RESTRICTED = "R"
    ADULTS = "NC-17"


class FilmAccessType(str, Enum):
    """Доступность фильма для просмотра."""

    PUBLIC = "public"
    SUBSCRIPTION = "subscription"


class FilmDetail(BaseIdOrjsonSchema):
    """Фильм."""

    title: str
    imdb_rating: float | None
    description: str
    release_date: datetime.date
    age_rating: FilmAgeRating
    access_type: FilmAccessType
    genre: list[GenreDetail]
    actors: list[PersonList]
    writers: list[PersonList]
    directors: list[PersonList]


class FilmList(BaseIdOrjsonSchema):
    """Список фильмов."""

    title: str
    imdb_rating: float | None
    access_type: FilmAccessType
