from uuid import UUID

import pytest

from tests.functional.utils.helpers import find_object_by_value

from ..base import BaseClientTest, CacheTestMixin, PaginationTestMixin


pytestmark = [pytest.mark.asyncio]


class TestFilmList(CacheTestMixin, PaginationTestMixin, BaseClientTest):
    """Тестирование получения списка фильмов."""

    endpoint = "/api/v1/films/"

    pagination_factory_name = "films_es"

    cache_field_name = "title"
    cache_es_fixture_name = "film_es"
    cache_dto_fixture_name = "film_dto"

    async def test_film_list_ok(self, films_es, films_dto):
        """Получение списка фильмов работает корректно."""
        fields_to_check = ("uuid", "title")

        got = await self.client.get("/api/v1/films")

        assert len(got) == len(films_dto)
        for field_to_check in fields_to_check:
            actual = set([film_data[field_to_check] for film_data in got])
            expected = set([(str(getattr(film, field_to_check))) for film in films_dto])
            assert actual == expected

    async def test_film_list_with_params(self, elastic, films_es, film_dto):
        """Список фильмов выводится корректно и с запросом с дополнительными параметрами."""
        genre = film_dto.genre[0]

        got = await self.client.get(f"/api/v1/films/?filter[genre]={genre.name}")

        assert len(got) == 1
        assert got[0]["uuid"] == str(film_dto.uuid)
        assert got[0]["title"] == film_dto.title

    async def test_film_list_from_cache_with_params(self, elastic, films_es, films_dto):
        """Кэширование списка фильмов корректно работает и в случае параметров в запросе."""
        sort_field = "imdb_rating"
        query = {"query": {"match_all": {}}}
        expected_es = await elastic.search(index="movies", body=query, sort=f"{sort_field}:desc")
        expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]
        film_dto = find_object_by_value(films_dto, "uuid", UUID(expected_uuid))
        new_title = "XXX"
        body = film_dto.dict()
        body["title"] = new_title
        request_url = f"/api/v1/films/?sort=-{sort_field}"

        from_source = await self.client.get(request_url)
        assert from_source[0]["uuid"] == expected_uuid

        await elastic.index(index="movies", doc_type="_doc", id=str(film_dto.uuid), body=body, refresh="wait_for")
        from_cache = await self.client.get(request_url)
        assert from_cache[0]["uuid"] == expected_uuid
        assert from_cache[0]["title"] != new_title
        assert from_cache[0]["title"] == film_dto.title
