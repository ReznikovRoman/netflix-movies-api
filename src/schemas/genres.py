from uuid import UUID, uuid4
from pydantic import Field
from .base import BaseOrjsonSchema


class Genre(BaseOrjsonSchema):
    """Жанры фильмов."""

    uuid: UUID = Field(default_factory=uuid4)
    name: str
    # TODO В описании задания "Основные сущности" у жанра есть признак "Популярность", вероятно надо добавить
    # rating: float
