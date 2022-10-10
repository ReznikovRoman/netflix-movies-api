from ..base import BaseClientTest, CacheTestMixin, NotFoundTestMixin
from .constants import PERSON_UUID


class TestPersonRetrieve(NotFoundTestMixin, CacheTestMixin, BaseClientTest):
    """Retrieving person full details by UUID."""

    endpoint = "/api/v1/persons/full/{uuid}"

    not_found_endpoint = f"/api/v1/persons/full/{PERSON_UUID}"

    cache_request_url = f"/api/v1/persons/full/{PERSON_UUID}"
    cache_es_index_name = "person"
    cache_field_name = "full_name"
    cache_es_fixture_name = "persons_full_es"
    cache_dto_fixture_name = "person_full_dto"

    async def test_person_ok(self, client, persons_full_es, person_full_dto):
        """Retrieving person full details by UUID works correctly."""
        got = await self.client.get(f"/api/v1/persons/full/{person_full_dto.uuid}")

        assert got["uuid"] == str(person_full_dto.uuid)
        assert got["full_name"] == person_full_dto.full_name
        assert got["roles"][0]["role"] == person_full_dto.roles[0].role
        assert len(got["roles"][0]["films"]) > 0
