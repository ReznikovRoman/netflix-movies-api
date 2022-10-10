import datetime
from enum import Enum

from movies.domain.genres import GenreDetail
from movies.domain.persons.schemas import PersonList
from movies.domain.schemas import BaseIdOrjsonSchema


class FilmAgeRating(str, Enum):
    """Film age rating.

    List of possible age ratings: https://bit.ly/3xuSpB0.
    """

    GENERAL = "G"
    PARENTAL_GUIDANCE = "PG"
    PARENTS = "PG-13"
    RESTRICTED = "R"
    ADULTS = "NC-17"


class FilmAccessType(str, Enum):
    """Film access type."""

    PUBLIC = "public"
    SUBSCRIPTION = "subscription"


class FilmDetail(BaseIdOrjsonSchema):
    """Film detail."""

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
    """Film list."""

    title: str
    imdb_rating: float | None
    access_type: FilmAccessType
