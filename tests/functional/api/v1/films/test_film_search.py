import pytest

from ..base import BaseClientTest, CacheTestMixin, CacheWithParamsSearchTestMixin, PaginationTestMixin


pytestmark = [pytest.mark.asyncio]


class TestFilmSearch(CacheTestMixin, PaginationTestMixin, BaseClientTest, CacheWithParamsSearchTestMixin):
    """Тестирование поиска по фильмам."""

    endpoint = "/api/v1/films/search/"

    pagination_factory_name = "films_es"
    pagination_request_params = {"query": "Title"}
    empty_request_params = {"query": "XXX"}

    cache_es_index_name = "movies"
    cache_field_name = "title"
    cache_es_fixture_name = "film_es"
    cache_dto_fixture_name = "film_dto"
    cache_request_params = {"query": "CustomFilm"}
    cache_dtos_fixture_name = "films_dto"
    cache_ess_fixture_name = "films_es"

    cache_search_fields = ["title", "description", "genres_names", "actors_names", "directors_names", "writers_names"]
    cache_search_query = "Title"
    cache_sort_field = "imdb_rating"
    cache_field_to_change = "title"

    async def test_film_search_ok(self, films_es, film_dto):
        """Поиск по фильмам работает корректно."""
        got = await self.client.get(f"/api/v1/films/search/?query={film_dto.title}")

        assert len(got) > 0
        assert got[0]["uuid"] == str(film_dto.uuid)

    async def test_film_search_no_results(self, films_es):
        """Если ни один фильм не найден по `query`, то возвращается пустой список."""
        got = await self.client.get("/api/v1/films/search/?query=XXX")

        assert len(got) == 0

    async def test_film_search_with_params(self, elastic, films_es):
        """Найденные фильмы выводятся в поиске корректно и с запросом с дополнительными параметрами."""
        sort_field = "imdb_rating"
        search_fields = ["title", "description", "genres_names", "actors_names", "directors_names", "writers_names"]
        search_query = "Title"
        query = {"query": {"multi_match": {"query": search_query, "fields": search_fields}}}
        expected_es = await elastic.search(index="movies", body=query, sort=f"{sort_field}")
        expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]

        got = await self.client.get(f"/api/v1/films/search/?query={search_query}&sort={sort_field}")

        assert len(got) == 4
        assert got[0]["uuid"] == expected_uuid
