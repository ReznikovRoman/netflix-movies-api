from movies.domain.schemas import BaseIdOrjsonSchema


class GenreDetail(BaseIdOrjsonSchema):
    """Жанр фильма."""

    name: str
