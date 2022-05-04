import pytest

from src.schemas.genres import GenreDetail


pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def genre_uuid():
    return "c7006f06-3ab2-4edf-92cd-92385716562e"


@pytest.fixture
def genre_dto(model_factory, genre_uuid) -> GenreDetail:
    return model_factory.create_factory(GenreDetail).build(uuid=genre_uuid)


@pytest.fixture
async def genre_es(elastic, genre_dto):
    await elastic.index(index="genre", doc_type="_doc", id=genre_dto.uuid, body=genre_dto.dict(), refresh="wait_for")
