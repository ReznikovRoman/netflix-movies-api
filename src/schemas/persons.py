from uuid import UUID, uuid4

from .base import BaseIdOrjsonSchema
from .films import MovieShortList


class PersonShortDetail(BaseIdOrjsonSchema):
    """Детализация участника фильма без указания роли."""

    full_name: str
    film_list: list[uuid4]


class PersonFullDetail(BaseIdOrjsonSchema):
    """Детализация участника фильма по ролям."""

    full_name: str
    films_as_director: list[MovieShortList]
    films_as_actor: list[MovieShortList]
    films_as_writer: list[MovieShortList]


class PersonList(BaseIdOrjsonSchema):
    """Список участников фильмов."""

    full_name: str
    film_ids: list[uuid4]
