from ..base import BaseClientTest, CacheTestMixin, NotFoundTestMixin
from .constants import PERSON_UUID


class TestPersonRetrieve(NotFoundTestMixin, CacheTestMixin, BaseClientTest):
    """Тестирование получения персоны по UUID."""

    endpoint = "/api/v1/persons/{uuid}"

    not_found_endpoint = f"/api/v1/persons/{PERSON_UUID}"

    cache_request_url = f"/api/v1/persons/{PERSON_UUID}"
    cache_es_index_name = "person"
    cache_field_name = "full_name"
    cache_es_fixture_name = "person_es"
    cache_dto_fixture_name = "person_dto"

    async def test_person_ok(self, client, person_es, person_dto):
        """Получение персоны по UUID работает корректно."""
        got = await self.client.get(f"/api/v1/persons/{person_dto.uuid}")

        assert got["uuid"] == str(person_dto.uuid)
        assert got["full_name"] == person_dto.full_name
