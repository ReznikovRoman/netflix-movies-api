import pytest

from ..base import BaseClientTest, NotFoundTestMixin
from .constants import FILM_UUID


pytestmark = [pytest.mark.asyncio]


class TestFilmRetrieve(NotFoundTestMixin, BaseClientTest):
    """Тестирование получения фильма по UUID."""

    endpoint = "/api/v1/films/{uuid}"

    not_found_endpoint = f"/api/v1/films/{FILM_UUID}"

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

    async def test_film_from_cache(self, elastic, film_es, film_dto):
        """Данные о фильме должны сохраняться в кэше после запроса в основную БД."""
        new_title = "XXX"
        body = film_dto.dict()
        body["title"] = new_title

        from_source = await self.client.get(f"/api/v1/films/{film_dto.uuid}")
        assert from_source["title"] == film_dto.title

        await elastic.index(index="movies", doc_type="_doc", id=str(film_dto.uuid), body=body, refresh="wait_for")
        from_cache = await self.client.get(f"/api/v1/films/{film_dto.uuid}")
        assert from_cache["title"] != new_title
        assert from_cache["title"] == film_dto.title
