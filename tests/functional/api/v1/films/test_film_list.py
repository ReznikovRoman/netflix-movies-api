from uuid import UUID

import pytest

from tests.functional.utils.helpers import find_object_by_value


pytestmark = [pytest.mark.asyncio]


async def test_film_list_ok(client, films_es, films_dto):
    """Получение списка фильмов работает корректно."""
    fields_to_check = ("uuid", "title")

    got = await client.get("/api/v1/films")

    assert len(got) == len(films_dto)
    for field_to_check in fields_to_check:
        actual = set([film_data[field_to_check] for film_data in got])
        expected = set([(str(getattr(film, field_to_check))) for film in films_dto])
        assert actual == expected


async def test_film_list_pagination(client, films_es, films_dto):
    """Пагинация фильмов работает корректно."""
    page_size = 3

    first_page = await client.get(f"/api/v1/films/?page[size]={page_size}")
    exact_page = await client.get(f"/api/v1/films/?page[size]={page_size}&page[number]=2")

    assert len(first_page) == 3
    assert len(exact_page) == 2


async def test_empty_response(client):
    """Если фильмов нет в основной БД, то должен выводиться пустой список."""
    got = await client.get("/api/v1/films")

    assert len(got) == 0


async def test_film_list_with_params(elastic, client, films_es, film_dto):
    """Список фильмов выводится корректно и с запросом с дополнительными параметрами."""
    genre = film_dto.genre[0]

    got = await client.get(f"/api/v1/films/?filter[genre]={genre.name}")

    assert len(got) == 1
    assert got[0]["uuid"] == str(film_dto.uuid)
    assert got[0]["title"] == film_dto.title


async def test_film_list_from_cache(elastic, client, film_es, film_dto):
    """Данные о списке фильмов должны сохраняться в кэше после запроса в основную БД."""
    new_title = "XXX"
    body = film_dto.dict()
    body["title"] = new_title

    from_source = await client.get("/api/v1/films")
    assert from_source[0]["title"] == film_dto.title

    await elastic.index(index="movies", doc_type="_doc", id=str(film_dto.uuid), body=body, refresh="wait_for")
    from_cache = await client.get("/api/v1/films")
    assert from_cache[0]["title"] != new_title
    assert from_cache[0]["title"] == film_dto.title


async def test_film_list_from_cache_with_params(elastic, client, films_es, films_dto):
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

    from_source = await client.get(request_url)
    assert from_source[0]["uuid"] == expected_uuid

    await elastic.index(index="movies", doc_type="_doc", id=str(film_dto.uuid), body=body, refresh="wait_for")
    from_cache = await client.get(request_url)
    assert from_cache[0]["uuid"] == expected_uuid
    assert from_cache[0]["title"] != new_title
    assert from_cache[0]["title"] == film_dto.title
