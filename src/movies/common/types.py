from typing import Type, Union
from uuid import UUID

from movies.domain.films import FilmDetail, FilmList
from movies.domain.genres import GenreDetail
from movies.domain.persons.schemas import PersonList, PersonShortDetail
from movies.domain.roles import PersonFullDetail

ApiSchema = Union[
    GenreDetail,
    FilmList,
    FilmDetail,
    PersonList,
    PersonShortDetail,
    PersonFullDetail,
]
ApiSchemaClass = Union[
    Type[GenreDetail],
    Type[FilmList],
    Type[FilmDetail],
    Type[PersonList],
    Type[PersonShortDetail],
    Type[PersonFullDetail],
]

seconds = int

Id = int | str | UUID

Query = dict | str
