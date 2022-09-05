import random

import pytest

from movies.domain.films.schemas import FilmAccessType, FilmDetail
from movies.domain.genres.schemas import GenreDetail
from tests.functional.api.v1.films.constants import (
    FILM_UUID, GENRE_UUID, SUBSCRIPTION_FILM_UUID, SUBSCRIPTION_GENRE_UUID,
)
from tests.functional.utils.helpers import add_film_document_to_elastic

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def film_uuid():
    return FILM_UUID


@pytest.fixture
def subscription_film_uuid():
    return SUBSCRIPTION_FILM_UUID


@pytest.fixture
def genre_uuid():
    return GENRE_UUID


@pytest.fixture
def subscription_genre_uuid():
    return SUBSCRIPTION_GENRE_UUID


@pytest.fixture
def film_dto(model_factory, film_uuid, genre_uuid) -> FilmDetail:
    genres = [GenreDetail(name="Test", uuid=genre_uuid)]
    film_ = model_factory.create_factory(FilmDetail).build(
        uuid=film_uuid, title="CustomFilm", genre=genres, access_type=FilmAccessType.PUBLIC.value)
    return film_


@pytest.fixture
def subscription_film_dto(model_factory, subscription_film_uuid, subscription_genre_uuid) -> FilmDetail:
    genres = [GenreDetail(name="SubscriptionGenre", uuid=subscription_genre_uuid)]
    film_ = model_factory.create_factory(FilmDetail).build(
        uuid=subscription_film_uuid, title="SubscriptionFilm", access_type=FilmAccessType.SUBSCRIPTION.value,
        genre=genres,
    )
    return film_


@pytest.fixture
def films_dto(model_factory, genre_uuid) -> list[FilmDetail]:
    names = [f"Title#{film_index}" for film_index in range(4)]
    films_ = model_factory.create_factory(
        FilmDetail, title=lambda: random.choice(names), access_type=FilmAccessType.PUBLIC.value).batch(size=4)
    return films_


@pytest.fixture
async def film_es(elastic, film_dto):
    await add_film_document_to_elastic(elastic, film_dto)


@pytest.fixture
async def subscription_film_es(elastic, subscription_film_dto):
    await add_film_document_to_elastic(elastic, subscription_film_dto)


@pytest.fixture
async def films_es(elastic, film_dto, films_dto):
    films_dto.append(film_dto)
    for film in films_dto:
        await add_film_document_to_elastic(elastic, film)
