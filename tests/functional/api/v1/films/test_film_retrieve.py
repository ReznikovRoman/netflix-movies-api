import pytest

from ..base import BaseClientTest, CacheTestMixin, NotFoundTestMixin
from .constants import FILM_UUID

pytestmark = [pytest.mark.asyncio]


class TestFilmRetrieve(NotFoundTestMixin, CacheTestMixin, BaseClientTest):
    """Тестирование получения фильма по UUID."""

    endpoint = "/api/v1/films/{uuid}"

    not_found_endpoint = f"/api/v1/films/{FILM_UUID}"

    cache_request_url = f"/api/v1/films/{FILM_UUID}"
    cache_es_index_name = "movies"
    cache_field_name = "title"
    cache_es_fixture_name = "film_es"
    cache_dto_fixture_name = "film_dto"

    async def test_film_ok(self, film_es, film_dto):
        """Получение фильма по UUID работает корректно."""
        got = await self.client.get(f"/api/v1/films/{film_dto.uuid}")

        assert got["uuid"] == str(film_dto.uuid)
        assert got["title"] == film_dto.title
        assert got["release_date"] == str(film_dto.release_date)
        assert got["age_rating"] == film_dto.age_rating.value
        assert all([
            str(expected_actor.uuid) == actual_actor["uuid"]
            for expected_actor, actual_actor in zip(film_dto.actors, got["actors"])
        ])
        assert all([
            str(expected_writer.uuid) == actual_writer["uuid"]
            for expected_writer, actual_writer in zip(film_dto.writers, got["writers"])
        ])
        assert all([
            str(expected_director.uuid) == actual_director["uuid"]
            for expected_director, actual_director in zip(film_dto.directors, got["directors"])
        ])
