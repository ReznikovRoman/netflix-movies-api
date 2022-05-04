import random

import pytest

from schemas.films import FilmDetail
from schemas.genres import GenreDetail
from tests.functional.utils.helpers import add_film_document_to_elastic


pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def film_uuid():
    return "797a60f4-f0aa-430f-bf1f-1145ec94d3a6"


@pytest.fixture
def genre_uuid():
    return "fddb2c25-3ac0-46d1-8e76-2ed6d63eec58"


@pytest.fixture
def film_dto(model_factory, film_uuid, genre_uuid) -> FilmDetail:
    genres = [GenreDetail(name="Test", uuid=genre_uuid)]
    return model_factory.create_factory(FilmDetail).build(uuid=film_uuid, genre=genres)


@pytest.fixture
def films_dto(model_factory, genre_uuid) -> list[FilmDetail]:
    names = [f"Title#{film_index}" for film_index in range(4)]
    return model_factory.create_factory(FilmDetail, title=lambda: random.choice(names)).batch(size=4)


@pytest.fixture
async def film_es(elastic, film_dto):
    await add_film_document_to_elastic(elastic, film_dto)


@pytest.fixture
async def films_es(elastic, film_dto, films_dto):
    films_dto.append(film_dto)
    for film in films_dto:
        await add_film_document_to_elastic(elastic, film)
