from uuid import UUID

from .base import BaseIdOrjsonSchema


class PersonShortDetail(BaseIdOrjsonSchema):
    """Персона (без информации о ролях)."""

    full_name: str
    film_ids: list[UUID]


class PersonList(BaseIdOrjsonSchema):
    """Список персон."""

    full_name: str
