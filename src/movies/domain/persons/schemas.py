from uuid import UUID

from movies.domain.schemas import BaseIdOrjsonSchema


class PersonShortDetail(BaseIdOrjsonSchema):
    """Person short detail (without roles)."""

    full_name: str
    films_ids: list[UUID]


class PersonList(BaseIdOrjsonSchema):
    """Person list."""

    full_name: str
