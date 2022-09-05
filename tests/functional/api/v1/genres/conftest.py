import random

import pytest

from movies.domain.genres.schemas import GenreDetail
from tests.functional.api.v1.genres.constants import GENRE_UUID

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def genre_uuid():
    return GENRE_UUID


@pytest.fixture
def genre_dto(model_factory, genre_uuid) -> GenreDetail:
    return model_factory.create_factory(GenreDetail).build(uuid=genre_uuid)


@pytest.fixture
def genres_dto(model_factory, genre_uuid) -> list[GenreDetail]:
    names = [f"Name#{genre_index}" for genre_index in range(4)]
    return model_factory.create_factory(GenreDetail, name=lambda: random.choice(names)).batch(size=4)


@pytest.fixture
async def genre_es(elastic, genre_dto):
    await elastic.index(index="genre", doc_type="_doc", id=genre_dto.uuid, body=genre_dto.dict(), refresh="wait_for")


@pytest.fixture
async def genres_es(elastic, genre_dto, genres_dto):
    genres_dto.append(genre_dto)
    for genre in genres_dto:
        await elastic.index(index="genre", doc_type="_doc", id=genre.uuid, body=genre.dict(), refresh="wait_for")
