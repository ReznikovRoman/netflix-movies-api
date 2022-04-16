from uuid import uuid4

from .base import BaseIdOrjsonSchema, BaseOrjsonSchema
from .films import MovieList


class PersonShortDetail(BaseIdOrjsonSchema):
    """Детализация участника фильма без указания роли."""

    full_name: str
    film_ids: list[uuid4]


class PersonRoleFilmList(BaseOrjsonSchema):
    """Роль участника с списком фильмов."""

    role: str
    films: list[MovieList]


class PersonFullDetail(BaseIdOrjsonSchema):
    """Детализация участника фильма по ролям."""

    full_name: str
    roles: list[PersonRoleFilmList]


class PersonList(BaseIdOrjsonSchema):
    """Список участников фильмов."""

    full_name: str
    film_ids: list[uuid4]
