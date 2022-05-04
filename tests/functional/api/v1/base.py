from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


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

    factory_name: str

    pagination_response_params: dict | None = None
    empty_response_params: dict | None = None

    @pytest.fixture(autouse=True)
    def _setup_pagination_params(self, client):
        if self.pagination_response_params is None:
            self.pagination_response_params = {}
        if self.empty_response_params is None:
            self.empty_response_params = {}

    @pytest.fixture
    def items(self, request, event_loop):
        # проблема с асинхронными фикстурами
        # ссылка на issue: https://github.com/pytest-dev/pytest-asyncio/issues/112#issuecomment-746031505
        request.getfixturevalue(self.factory_name)

    async def test_pagination(self, items):
        """Пагинация объектов работает корректно."""
        page_size = 3

        first_page = await self.client.get(
            f"{self.endpoint}", params={"page[size]": page_size, **self.pagination_response_params})
        exact_page = await self.client.get(
            f"{self.endpoint}", params={"page[size]": page_size, "page[number]": 2, **self.pagination_response_params})

        assert len(first_page) == 3, first_page
        assert len(exact_page) > 0

    async def test_empty_response(self):
        """Если объектов нет в основной БД, то должен выводиться пустой список."""
        got = await self.client.get(self.endpoint, params=self.empty_response_params)

        assert len(got) == 0


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
