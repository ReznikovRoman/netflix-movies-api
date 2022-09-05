from uuid import UUID

from movies.domain.schemas import BaseIdOrjsonSchema


class PersonShortDetail(BaseIdOrjsonSchema):
    """Персона (без информации о ролях)."""

    full_name: str
    films_ids: list[UUID]


class PersonList(BaseIdOrjsonSchema):
    """Список персон."""

    full_name: str