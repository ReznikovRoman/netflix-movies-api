import random

import pytest

from src.schemas.films import FilmDetail, FilmList
from src.schemas.genres import GenreDetail
from src.schemas.persons import PersonList, PersonShortDetail
from src.schemas.roles import PersonFullDetail, PersonRoleFilmList
from tests.functional.api.v1.films.constants import FILM_UUID
from tests.functional.api.v1.genres.constants import GENRE_UUID
from tests.functional.api.v1.persons.constants import PERSON_UUID, PERSON_UUID_OTHER


pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def person_uuid():
    return PERSON_UUID


@pytest.fixture
def person_uuid_other():
    return PERSON_UUID_OTHER


@pytest.fixture
def film_uuid():
    return FILM_UUID


@pytest.fixture
def genre_uuid():
    return GENRE_UUID


@pytest.fixture
def person_dto(model_factory, person_uuid) -> PersonShortDetail:
    return model_factory.create_factory(PersonShortDetail).build(uuid=person_uuid, full_name="CustomPerson")


@pytest.fixture
def person_full_dto(model_factory, person_uuid, film_uuid) -> PersonFullDetail:
    roles = [PersonRoleFilmList(role="actor", films=[FilmList(title="title", uuid=film_uuid)])]
    return model_factory.create_factory(PersonFullDetail).build(
        uuid=person_uuid, full_name="CustomPerson", roles=roles)


@pytest.fixture
def persons_dto(model_factory, person_uuid) -> list[PersonShortDetail]:
    names = [f"Name#{person_index}" for person_index in range(4)]
    return model_factory.create_factory(PersonShortDetail, full_name=lambda: random.choice(names)).batch(size=4)


@pytest.fixture
async def person_es(elastic, person_dto):
    await elastic.index(
        index="person", doc_type="_doc", id=person_dto.uuid, body=person_dto.dict(), refresh="wait_for")


@pytest.fixture
async def persons_es(elastic, person_dto, persons_dto):
    persons_dto.append(person_dto)
    for person in persons_dto:
        await elastic.index(
            index="person", doc_type="_doc", id=person.uuid, body=person.dict(), refresh="wait_for")


@pytest.fixture
async def persons_full_es(elastic, person_dto, person_full_dto):
    await elastic.index(
        index="person", doc_type="_doc", id=person_full_dto.uuid, body=person_full_dto.dict(), refresh="wait_for")


@pytest.fixture
def film_dto(model_factory, film_uuid, genre_uuid, person_uuid_other) -> FilmDetail:
    genres = [GenreDetail(name="Test", uuid=genre_uuid)]
    actors = [PersonList(uuid=person_uuid_other, full_name="Cached")]
    return model_factory.create_factory(FilmDetail).build(
        uuid=film_uuid, title="CustomFilm", genre=genres, actors=actors)


@pytest.fixture
def films_dto(model_factory, genre_uuid) -> list[FilmList]:
    names = [f"Title#{film_index}" for film_index in range(4)]
    return model_factory.create_factory(FilmList, title=lambda: random.choice(names)).batch(size=4)


@pytest.fixture
async def films_es(elastic, film_dto, films_dto):
    body = film_dto.dict()
    body["actors_names"] = [actor.full_name for actor in film_dto.actors]
    await elastic.index(index="movies", doc_type="_doc", id=film_dto.uuid, body=body, refresh="wait_for")
    for film in films_dto:
        await elastic.index(index="movies", doc_type="_doc", id=film.uuid, body=film.dict(), refresh="wait_for")


@pytest.fixture
async def film_es(elastic, film_dto):
    await elastic.index(index="movies", doc_type="_doc", id=film_dto.uuid, body=film_dto.dict(), refresh="wait_for")
