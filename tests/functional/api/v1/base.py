from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from tests.functional.utils.helpers import find_object_by_value


if TYPE_CHECKING:
    from tests.functional.testlib import APIClient


pytestmark = [pytest.mark.asyncio]


class BaseClientTest:
    """Базовый тестовый класс."""

    client: APIClient
    endpoint: str

    @pytest.fixture(autouse=True)
    def _setup(self, client):
        self.client: APIClient = client
        self.endpoint = self.endpoint.removesuffix("/")


class PaginationTestMixin:
    """Миксин для тестов на пагинацию."""

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
        # XXX: проблема с асинхронными фикстурами в pytest-asyncio.
        # https://github.com/pytest-dev/pytest-asyncio/issues/112#issuecomment-746031505
        request.getfixturevalue(self.pagination_factory_name)

    async def test_pagination(self, items):
        """Пагинация объектов работает корректно."""
        page_size = 3

        first_page = await self.client.get(
            f"{self.endpoint}", params={"page[size]": page_size, **self.pagination_request_params})
        exact_page = await self.client.get(
            f"{self.endpoint}", params={"page[size]": page_size, "page[number]": 2, **self.pagination_request_params})

        assert len(first_page) == 3
        assert len(exact_page) > 0

    async def test_empty_response(self):
        """Если объектов нет в основной БД, то должен выводиться пустой список."""
        got = await self.client.get(self.endpoint, params=self.empty_request_params)

        assert len(got) == 0


class CacheTestMixin:
    """Миксин для тестов на корректную работу кэша."""

    cache_field_name: str
    cache_es_fixture_name: str
    cache_dto_fixture_name: str
    cache_es_index_name: str

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
        """Данные об объекте должны сохраняться в кэше после запроса в основную БД."""
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
    """Миксин с параметрами для тестов на корректную работу кэша."""

    cache_field_name: str
    cache_es_fixture_name: str
    cache_dto_fixture_name: str
    cache_dtos_fixture_name: str
    cache_es_index_name: str
    cache_ess_fixture_name: str

    cache_request_url: str | None = None
    cache_obj_id_field: str = "uuid"
    cache_request_params: dict | None = None

    cache_sort_field: str
    cache_query: dict | None = None
    cache_field_to_change: str

    @pytest.fixture
    def obj_dto(self, request, event_loop):
        return request.getfixturevalue(self.cache_dto_fixture_name)

    @pytest.fixture
    def objs_dto(self, request, event_loop):
        return request.getfixturevalue(self.cache_dtos_fixture_name)

    @pytest.fixture
    def obj_es(self, request, event_loop):
        return request.getfixturevalue(self.cache_es_fixture_name)

    @pytest.fixture
    def objs_es(self, request, event_loop):
        return request.getfixturevalue(self.cache_ess_fixture_name)

    @pytest.mark.usefixtures("elastic")
    async def test_obj_from_cache_with_params(self, elastic, objs_dto, objs_es):
        # TODO Вероятно uuid надо поменять на cache_obj_id_field
        expected_es = await elastic.search(
            index=self.cache_es_index_name, body=self.cache_query, sort=f"{self.cache_sort_field}:desc",
        )
        expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]
        obj_dto = find_object_by_value(objs_dto, "uuid", UUID(expected_uuid))
        new_data = "XXX"
        body = obj_dto.dict()
        body[self.cache_field_to_change] = new_data
        request_url = f"{self.endpoint}?sort=-{self.cache_sort_field}"

        from_source = await self.client.get(request_url)
        assert from_source[0]["uuid"] == expected_uuid

        await elastic.index(
            index=self.cache_es_index_name, doc_type="_doc", id=str(obj_dto.uuid), body=body, refresh="wait_for",
        )
        from_cache = await self.client.get(request_url)
        assert from_cache[0]["uuid"] == expected_uuid
        assert from_cache[0][self.cache_field_to_change] != new_data
        assert from_cache[0][self.cache_field_to_change] == getattr(obj_dto, self.cache_field_to_change)


class CacheWithParamsSearchTestMixin:
    """Миксин с параметрами поиска для тестов на корректную работу кэша."""

    cache_field_name: str
    cache_es_fixture_name: str
    cache_dto_fixture_name: str
    cache_dtos_fixture_name: str
    cache_es_index_name: str
    cache_ess_fixture_name: str

    cache_request_url: str | None = None
    cache_obj_id_field: str = "uuid"
    cache_request_params: dict | None = None

    cache_search_fields: list[str]
    cache_search_query: str
    cache_sort_field: str
    cache_field_to_change: str

    @pytest.fixture
    def obj_dto(self, request, event_loop):
        return request.getfixturevalue(self.cache_dto_fixture_name)

    @pytest.fixture
    def objs_dto(self, request, event_loop):
        return request.getfixturevalue(self.cache_dtos_fixture_name)

    @pytest.fixture
    def obj_es(self, request, event_loop):
        return request.getfixturevalue(self.cache_es_fixture_name)

    @pytest.fixture
    def objs_es(self, request, event_loop):
        return request.getfixturevalue(self.cache_ess_fixture_name)

    async def test_obj_search_from_cache_with_params(self, elastic, objs_es, objs_dto):
        """Кэширование найденных фильмов корректно работает и в случае параметров в запросе."""
        # TODO Вероятно uuid надо поменять на cache_obj_id_field
        query = {"query": {"multi_match": {"query": self.cache_search_query, "fields": self.cache_search_fields}}}
        expected_es = await elastic.search(
            index=self.cache_es_index_name, body=query, sort=f"{self.cache_sort_field}:desc",
        )
        expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]
        obj_dto = find_object_by_value(objs_dto, "uuid", UUID(expected_uuid))
        new_title = "XXX"
        body = obj_dto.dict()
        body[self.cache_field_to_change] = new_title
        request_url = f"{self.endpoint}/?query={self.cache_search_query}&sort=-{self.cache_sort_field}"

        from_source = await self.client.get(request_url)
        assert from_source[0]["uuid"] == expected_uuid

        await elastic.index(
            index=self.cache_es_index_name, doc_type="_doc", id=str(obj_dto.uuid), body=body, refresh="wait_for",
        )
        from_cache = await self.client.get(request_url)
        assert from_cache[0]["uuid"] == expected_uuid
        assert from_cache[0][self.cache_field_to_change] != new_title
        assert from_cache[0][self.cache_field_to_change] == obj_dto.title


class NotFoundTestMixin:
    """Миксин для тестов на ненайденный объект."""

    not_found_endpoint: str

    def get_not_found_endpoint(self, *args, **kwargs):
        if self.not_found_endpoint is not None:
            return self.not_found_endpoint

    async def test_not_found(self):
        """Если запрашиваемый ресурс не найден, то возвращается ответ с корректным сообщением и 404 статусом."""
        got = await self.client.get(self.get_not_found_endpoint(), expected_status_code=404)

        assert "not found" in got["detail"]
