import pytest

from src.schemas.films import FilmDetail


pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def film_uuid():
    return "797a60f4-f0aa-430f-bf1f-1145ec94d3a6"


@pytest.fixture
def film_dto(model_factory, film_uuid) -> FilmDetail:
    return model_factory.create_factory(FilmDetail).build(uuid=film_uuid)


@pytest.fixture
async def film_es(elastic, film_dto):
    await elastic.index(index="movies", doc_type="_doc", id=film_dto.uuid, body=film_dto.dict(), refresh="wait_for")
