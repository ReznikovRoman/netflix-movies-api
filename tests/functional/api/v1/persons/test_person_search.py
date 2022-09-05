import pytest

from ..base import BaseClientTest, CacheTestMixin, CacheWithParamsTestMixin, PaginationTestMixin

pytestmark = [pytest.mark.asyncio]


class TestPersonSearch(
    CacheWithParamsTestMixin,
    CacheTestMixin,
    PaginationTestMixin,
    BaseClientTest,
):
    """Тестирование поиска по персонам."""

    endpoint = "/api/v1/persons/search/"

    pagination_factory_name = "persons_es"
    pagination_request_params = {"query": "Name"}
    empty_request_params = {"query": "XXX"}

    cache_field_name = "full_name"
    cache_es_index_name = "person"
    cache_es_fixture_name = "person_es"
    cache_dto_fixture_name = "person_dto"
    cache_request_params = {"query": "CustomPerson"}

    _search_fields = ["full_name"]
    _search_query = "Name"
    cache_es_query = {"query": {"multi_match": {"query": _search_query, "fields": _search_fields}}}
    cache_es_list_fixture_name = "persons_es"
    cache_dto_list_fixture_name = "persons_dto"
    cache_with_params_request = {"query": _search_query}

    async def test_person_search_ok(self, elastic, persons_es):
        """Найденные персоны выводятся в поиске корректно."""
        search_fields = ["full_name"]
        search_query = "Name"
        query = {"query": {"multi_match": {"query": search_query, "fields": search_fields}}}
        expected_es = await elastic.search(index="person", body=query)
        expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]

        got = await self.client.get(f"/api/v1/persons/search/?query={search_query}")

        assert len(got) == 4
        assert got[0]["uuid"] == expected_uuid

    async def test_person_search_no_results(self, persons_es):
        """Если ни одна персона не найдена по `query`, то возвращается пустой список."""
        got = await self.client.get("/api/v1/persons/search/?query=XXX")

        assert len(got) == 0
