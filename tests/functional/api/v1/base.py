from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from tests.functional.utils.helpers import find_object_by_value

if TYPE_CHECKING:
    from tests.functional.testlib import APIClient


pytestmark = [pytest.mark.asyncio]


class BaseClientTest:
    """Base test class."""

    client: APIClient
    endpoint: str

    @pytest.fixture(autouse=True)
    def _setup(self, client):
        self.client: APIClient = client
        self.endpoint = self.endpoint.removesuffix("/")


class PaginationTestMixin:
    """Mixin for pagination tests."""

    pagination_factory_name: str

    pagination_request_params: dict | None = None
    empty_request_params: dict | None = None

    @pytest.fixture(autouse=True)
    def _setup_pagination_params(self):
        if self.pagination_request_params is None:
            self.pagination_request_params = {}
        if self.empty_request_params is None:
            self.empty_request_params = {}

    @pytest.fixture
    def items(self, request, event_loop):
        # XXX: problem with async fixtures in pytest-asyncio.
        # https://github.com/pytest-dev/pytest-asyncio/issues/112#issuecomment-746031505
        request.getfixturevalue(self.pagination_factory_name)

    async def test_pagination(self, items):
        """Items pagination works correctly."""
        page_size = 3

        first_page = await self.client.get(
            f"{self.endpoint}", params={"page[size]": page_size, **self.pagination_request_params})
        exact_page = await self.client.get(
            f"{self.endpoint}", params={"page[size]": page_size, "page[number]": 2, **self.pagination_request_params})

        assert len(first_page) == 3, first_page
        assert len(exact_page) > 0

    @pytest.mark.usefixtures("elastic")
    async def test_empty_response(self, elastic):
        """If there are no items in the DB, an empty list is returned."""
        got = await self.client.get(self.endpoint, params=self.empty_request_params)

        assert len(got) == 0


class CacheTestMixin:
    """Mixin for cache related tests."""

    cache_field_name: str
    cache_es_index_name: str
    cache_es_fixture_name: str
    cache_dto_fixture_name: str

    cache_request_url: str | None = None
    cache_obj_id_field: str = "uuid"
    cache_request_params: dict | None = None

    @pytest.fixture(autouse=True)
    def _setup_cache_params(self):
        if self.cache_request_params is None:
            self.cache_request_params = {}

    @pytest.fixture
    def obj_dto(self, request, event_loop):
        return request.getfixturevalue(self.cache_dto_fixture_name)

    @pytest.fixture
    def obj_es(self, request, event_loop):
        return request.getfixturevalue(self.cache_es_fixture_name)

    @pytest.mark.usefixtures("elastic")
    async def test_obj_from_cache(self, elastic, obj_dto, obj_es):
        """Item should be saved in cache after request to the primary database."""
        request_url = self.cache_request_url or self.endpoint

        new_value = "XXX"
        body = obj_dto.dict()
        body[self.cache_field_name] = new_value
        obj_id = str(getattr(obj_dto, self.cache_obj_id_field))

        from_source = await self.client.get(request_url, params=self.cache_request_params)
        if isinstance(from_source, list):
            from_source = from_source[0]
        assert from_source[self.cache_field_name] == getattr(obj_dto, self.cache_field_name)

        await elastic.index(index=self.cache_es_index_name, doc_type="_doc", id=obj_id, body=body, refresh="wait_for")
        from_cache = await self.client.get(request_url, params=self.cache_request_params)
        if isinstance(from_cache, list):
            from_cache = from_cache[0]
        assert from_cache[self.cache_field_name] != new_value
        assert from_cache[self.cache_field_name] == getattr(obj_dto, self.cache_field_name)


class CacheWithParamsTestMixin:
    """Mixin for cache related (with custom query parameters) tests."""

    # from `CacheTestMixin`
    cache_field_name: str
    cache_es_index_name: str
    cache_es_fixture_name: str
    cache_dto_fixture_name: str
    cache_request_url: str | None = None
    cache_obj_id_field: str = "uuid"
    cache_request_params: dict | None = None

    cache_es_query: str
    cache_es_params: dict | None = None
    cache_es_list_fixture_name: str
    cache_dto_list_fixture_name: str
    cache_with_params_request: dict

    @pytest.fixture(autouse=True)
    def _setup_cache_es_params(self):
        if self.cache_es_params is None:
            self.cache_es_params = {}

    @pytest.fixture
    def objs_dto(self, request, event_loop):
        return request.getfixturevalue(self.cache_dto_list_fixture_name)

    @pytest.fixture
    def objs_es(self, request, event_loop):
        return request.getfixturevalue(self.cache_es_list_fixture_name)

    @pytest.mark.usefixtures("elastic")
    async def test_obj_list_from_cache_with_params(self, elastic, objs_es, objs_dto):
        """Caching list of items works correctly with query parameters in a request."""
        request_url = self.cache_request_url or self.endpoint
        expected_es = await elastic.search(
            index=self.cache_es_index_name, body=self.cache_es_query, **self.cache_es_params)
        expected_uuid = expected_es["hits"]["hits"][0]["_source"][self.cache_obj_id_field]
        obj_dto = find_object_by_value(objs_dto, self.cache_obj_id_field, UUID(expected_uuid))
        new_value = "XXX"
        body = obj_dto.dict()
        body[self.cache_field_name] = new_value

        from_source = await self.client.get(request_url, params=self.cache_with_params_request)
        assert from_source[0][self.cache_obj_id_field] == expected_uuid

        await elastic.index(
            index=self.cache_es_index_name,
            doc_type="_doc",
            id=str(getattr(obj_dto, self.cache_obj_id_field)),
            body=body,
            refresh="wait_for",
        )
        from_cache = await self.client.get(request_url, params=self.cache_with_params_request)
        assert from_cache[0][self.cache_obj_id_field] == expected_uuid
        assert from_cache[0][self.cache_field_name] != new_value
        assert from_cache[0][self.cache_field_name] == getattr(obj_dto, self.cache_field_name)


class NotFoundTestMixin:
    """Mixin for 'missing item' tests."""

    not_found_endpoint: str

    def get_not_found_endpoint(self, *args, **kwargs):
        if self.not_found_endpoint is not None:
            return self.not_found_endpoint

    @pytest.mark.usefixtures("elastic")
    async def test_not_found(self, elastic):
        """If the requested item is not found, response with a correct message and 404 status is returned."""
        got = await self.client.get(self.get_not_found_endpoint(), expected_status_code=404)

        assert "error" in got
