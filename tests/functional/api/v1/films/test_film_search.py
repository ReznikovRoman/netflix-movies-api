from uuid import UUID

import pytest

from tests.functional.utils.helpers import find_object_by_value


pytestmark = [pytest.mark.asyncio]


async def test_film_search_ok(client, films_es, film_dto):
    """Поиск по фильмам работает корректно."""
    got = await client.get(f"/api/v1/films/search/?query={film_dto.title}")

    assert len(got) > 0
    assert got[0]["uuid"] == str(film_dto.uuid)


async def test_film_search_no_results(client, films_es):
    """Если ни один фильм не найден по `query`, то возвращается пустой список."""
    got = await client.get("/api/v1/films/search/?query=XXX")

    assert len(got) == 0


async def test_film_search_pagination(client, films_es):
    """Пагинация по найденным фильмам работает корректно."""
    page_size = 3

    first_page = await client.get(f"/api/v1/films/search/?query=Title&page[size]={page_size}")
    exact_page = await client.get(f"/api/v1/films/search/?query=Title&page[size]={page_size}&page[number]=2")

    assert len(first_page) == 3
    assert len(exact_page) == 1


async def test_empty_response(client):
    """Если фильмов нет в основной БД, то должен выводиться пустой список."""
    got = await client.get("/api/v1/films/search/?query=XXX")

    assert len(got) == 0


async def test_film_search_with_params(elastic, client, films_es):
    """Найденные фильмы выводятся в поиске корректно и с запросом с дополнительными параметрами."""
    sort_field = "imdb_rating"
    search_fields = ["title", "description", "genres_names", "actors_names", "directors_names", "writers_names"]
    search_query = "Title"
    query = {"query": {"multi_match": {"query": search_query, "fields": search_fields}}}
    expected_es = await elastic.search(index="movies", body=query, sort=f"{sort_field}")
    expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]

    got = await client.get(f"/api/v1/films/search/?query={search_query}&sort={sort_field}")

    assert len(got) == 4
    assert got[0]["uuid"] == expected_uuid


async def test_film_search_from_cache(elastic, client, film_es, film_dto):
    """Данные о найденных фильмах должны сохраняться в кэше после запроса в основную БД."""
    new_title = "XXX"
    body = film_dto.dict()
    body["title"] = new_title
    request_url = f"/api/v1/films/search/?query={film_dto.title}"

    from_source = await client.get(request_url)
    assert from_source[0]["title"] == film_dto.title

    await elastic.index(index="movies", doc_type="_doc", id=str(film_dto.uuid), body=body, refresh="wait_for")
    from_cache = await client.get(request_url)
    assert from_cache[0]["title"] != new_title
    assert from_cache[0]["title"] == film_dto.title


async def test_film_search_from_cache_with_params(elastic, client, films_es, films_dto):
    """Кэширование найденных фильмов корректно работает и в случае параметров в запросе."""
    sort_field = "imdb_rating"
    search_fields = ["title", "description", "genres_names", "actors_names", "directors_names", "writers_names"]
    search_query = "Title"
    query = {"query": {"multi_match": {"query": search_query, "fields": search_fields}}}
    expected_es = await elastic.search(index="movies", body=query, sort=f"{sort_field}:desc")
    expected_uuid = expected_es["hits"]["hits"][0]["_source"]["uuid"]
    film_dto = find_object_by_value(films_dto, "uuid", UUID(expected_uuid))
    new_title = "XXX"
    body = film_dto.dict()
    body["title"] = new_title
    request_url = f"/api/v1/films/search/?query={search_query}&sort=-{sort_field}"

    from_source = await client.get(request_url)
    assert from_source[0]["uuid"] == expected_uuid

    await elastic.index(index="movies", doc_type="_doc", id=str(film_dto.uuid), body=body, refresh="wait_for")
    from_cache = await client.get(request_url)
    assert from_cache[0]["uuid"] == expected_uuid
    assert from_cache[0]["title"] != new_title
    assert from_cache[0]["title"] == film_dto.title
