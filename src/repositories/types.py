from typing import Union

from .films import FilmRepository
from .genres import GenreRepository
from .persons import PersonRepository


Repository = Union[
    GenreRepository,
    FilmRepository,
    PersonRepository,
]
