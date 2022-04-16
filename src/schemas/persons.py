from uuid import UUID, uuid4
from pydantic import Field
from .base import BaseOrjsonSchema
from .genres import Genre
from .films import MovieList

class PersonDetail(BaseOrjsonSchema):
    """Детализация участника фильма"""

    uuid: UUID = Field(default_factory=uuid4)
    full_name: str
    role: str # TODO Пока остается открытым вопрос когда в списке фильмов участник под разными ролями
    film_list: list[MovieList]

class PersonList(BaseOrjsonSchema):
    """Список участников фильмов"""
    
    uuid: UUID = Field(default_factory=uuid4)
    full_name: str
    film_list: list[MovieList]