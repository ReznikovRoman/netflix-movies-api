import pytest

from ..base import BaseClientTest, CacheTestMixin, CacheWithParamsTestMixin, PaginationTestMixin


pytestmark = [pytest.mark.asyncio]


class TestFilmList(
    CacheWithParamsTestMixin,
    CacheTestMixin,
    PaginationTestMixin,
    BaseClientTest,
):
    """Тестирование получения списка фильмов."""

    endpoint = "/api/v1/films/"

    pagination_factory_name = "films_es"

    cache_field_name = "title"
    cache_es_index_name = "movies"
    cache_es_fixture_name = "film_es"
    cache_dto_fixture_name = "film_dto"

    cache_es_query = {"query": {"match_all": {}}}
    cache_es_params = {"sort": "imdb_rating:desc"}
    cache_es_list_fixture_name = "films_es"
    cache_dto_list_fixture_name = "films_dto"
    cache_with_params_request = {"sort": "-imdb_rating"}

    async def test_film_list_ok(self, films_es, films_dto):
        """Получение списка фильмов работает корректно."""
        fields_to_check = ("uuid", "title")

        got = await self.client.get("/api/v1/films")

        assert len(got) == len(films_dto)
        for field_to_check in fields_to_check:
            actual = set([film_data[field_to_check] for film_data in got])
            expected = set([(str(getattr(film, field_to_check))) for film in films_dto])
            assert actual == expected

    async def test_film_list_with_params(self, elastic, films_es, film_dto):
        """Список фильмов выводится корректно и с запросом с дополнительными параметрами."""
        genre = film_dto.genre[0]

        got = await self.client.get(f"/api/v1/films/?filter[genre]={genre.name}")

        assert len(got) == 1
        assert got[0]["uuid"] == str(film_dto.uuid)
        assert got[0]["title"] == film_dto.title
