from ..base import BaseClientTest, CacheTestMixin, NotFoundTestMixin
from .constants import GENRE_UUID


class TestGenreRetrieve(NotFoundTestMixin, CacheTestMixin, BaseClientTest):
    """Tests for retrieving genre details by UUID."""

    endpoint = "/api/v1/genres/{uuid}"

    not_found_endpoint = f"/api/v1/genres/{GENRE_UUID}"

    cache_request_url = f"/api/v1/genres/{GENRE_UUID}"
    cache_es_index_name = "genre"
    cache_field_name = "name"
    cache_es_fixture_name = "genre_es"
    cache_dto_fixture_name = "genre_dto"

    async def test_genre_ok(self, client, genre_es, genre_dto):
        """Retrieving genre by UUID works correctly."""
        got = await self.client.get(f"/api/v1/genres/{genre_dto.uuid}")

        assert got["uuid"] == str(genre_dto.uuid)
        assert got["name"] == genre_dto.name
