from enum import Enum

from .base import BaseIdOrjsonSchema, BaseOrjsonSchema
from .movies import MovieList


class Role(str, Enum):
    """Роль персоны."""

    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"


class PersonRoleFilmList(BaseOrjsonSchema):
    """Роль персоны со списком фильмов."""

    role: Role
    films: list[MovieList]


class PersonFullDetail(BaseIdOrjsonSchema):
    """Персона (с разбиением фильмов по ролям)."""

    full_name: str
    roles: list[PersonRoleFilmList]
