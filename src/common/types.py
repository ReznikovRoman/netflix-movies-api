from typing import Type, Union

from schemas.films import FilmDetail, FilmList
from schemas.genres import GenreDetail
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail


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
