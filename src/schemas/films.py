from uuid import UUID, uuid4
from pydantic import Field
from .base import BaseOrjsonSchema
from .genres import Genre
from .persons import PersonList
from datetime import date

class MovieDetail(BaseOrjsonSchema):
    """Детализация фильма"""
    
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    imdb_rating: float
    description: str
    created_at: date
    age_limit: int
    genre: list[Genre]
    actors: list[PersonList]
    writers: list[PersonList]
    directors: list[PersonList]
    # TODO Ссылка на картинку для превью
    # TODO В скриншоте задания есть так же информация о длине фильма, добавляем? length_in_mins: int
    # TODO Вероятно нам так же нужно тут выводить деление по типу (Фильм/Сериал)

class MovieList(BaseOrjsonSchema):
    """Список фильмов"""
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    imdb_rating: float
    # TODO Ссылка на картинку для превью