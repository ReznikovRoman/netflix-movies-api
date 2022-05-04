from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from tests.functional.testlib import APIClient


pytestmark = [pytest.mark.asyncio]


class BaseClientTest:
    """Базовый тестовый класс."""

    client: APIClient

    @pytest.fixture(autouse=True)
    def _setup(self, client):
        self.client: APIClient = client


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
