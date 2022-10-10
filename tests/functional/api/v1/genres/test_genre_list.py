from ..base import BaseClientTest, CacheTestMixin


class TestGenreList(CacheTestMixin, BaseClientTest):
    """Tests for retrieving a list of genres."""

    endpoint = "/api/v1/genres/"

    cache_es_index_name = "genre"
    cache_field_name = "name"
    cache_es_fixture_name = "genre_es"
    cache_dto_fixture_name = "genre_dto"

    async def test_genre_list_ok(self, genres_es, genres_dto):
        """Retrieving list of genres works correctly."""
        fields_to_check = ("uuid", "name")

        got = await self.client.get("/api/v1/genres")

        assert len(got) == len(genres_dto)
        for field_to_check in fields_to_check:
            actual = set([genre_data[field_to_check] for genre_data in got])
            expected = set([(str(getattr(genre, field_to_check))) for genre in genres_dto])
            assert actual == expected
