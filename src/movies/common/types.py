from typing import Type, Union
from uuid import UUID

from movies.schemas.films import FilmDetail, FilmList
from movies.schemas.genres import GenreDetail
from movies.schemas.persons import PersonList, PersonShortDetail
from movies.schemas.roles import PersonFullDetail

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
