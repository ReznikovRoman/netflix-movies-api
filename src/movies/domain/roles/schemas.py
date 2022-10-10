from enum import Enum

from movies.domain.films.schemas import FilmList
from movies.domain.schemas import BaseIdOrjsonSchema, BaseOrjsonSchema


class Role(str, Enum):
    """Person role."""

    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"


class PersonRoleFilmList(BaseOrjsonSchema):
    """Person role with associated films."""

    role: Role
    films: list[FilmList]


class PersonFullDetail(BaseIdOrjsonSchema):
    """Person full detail (with films by roles)."""

    full_name: str
    roles: list[PersonRoleFilmList]
