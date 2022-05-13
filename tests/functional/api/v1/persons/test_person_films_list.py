from ..base import BaseClientTest, CacheTestMixin
from .constants import PERSON_UUID_OTHER


class TestPersonFilmList(CacheTestMixin, BaseClientTest):
    """Тестирование получения списка фильмов по UUID персоны."""

    endpoint = "/api/v1/persons/{uuid}/films"

    cache_request_url = f"/api/v1/persons/{PERSON_UUID_OTHER}/films"
    cache_es_index_name = "movies"
    cache_field_name = "title"
    cache_es_fixture_name = "film_es"
    cache_dto_fixture_name = "film_dto"

    async def test_person_film_list_ok(self, client, films_es, film_dto, person_es, person_uuid_other):
        """Получение списка фильмов по UUID персоны работает корректно."""
        got = await self.client.get(f"/api/v1/persons/{person_uuid_other}/films")

        assert len(got) == 1
        assert got[0]["uuid"] == str(film_dto.uuid)
        assert got[0]["title"] == film_dto.title
