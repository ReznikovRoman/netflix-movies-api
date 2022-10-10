from movies.domain.schemas import BaseIdOrjsonSchema


class GenreDetail(BaseIdOrjsonSchema):
    """Genre detail."""

    name: str
