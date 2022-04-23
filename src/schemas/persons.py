from uuid import UUID

from .base import BaseIdOrjsonSchema


class PersonShortDetail(BaseIdOrjsonSchema):
    """Персона (без информации о ролях)."""

    full_name: str
    films_ids: list[UUID]  # films_ids: list[UUID] i gues we need to change index we got string of ids in index


class PersonList(BaseIdOrjsonSchema):
    """Список персон."""

    full_name: str
