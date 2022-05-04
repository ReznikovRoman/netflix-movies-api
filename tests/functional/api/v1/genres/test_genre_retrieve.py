
async def test_genre_single(client, genre_es, genre_dto):
    """Получение жанра по UUID."""
    got = await client.get(f"/api/v1/genres/{genre_dto.uuid}")

    assert got["uuid"] == str(genre_dto.uuid)
    assert got["name"] == genre_dto.name


async def test_genre_list(client, genre_es, genre_dto):
    """Получение списка жанров."""
    got = await client.get("/api/v1/genres/")
    assert len(got) == 1
    assert got[0]["uuid"] == str(genre_dto.uuid)
    assert got[0]["name"] == genre_dto.name


async def test_genre_not_found(client, genre_uuid):
    """Если жанр не найден, то должен возвращаться ответ с корректным сообщением и 404 статусом."""
    got = await client.get(f"/api/v1/genres/{genre_uuid}", expected_status_code=404)

    assert "genre not found" in got["detail"]


async def test_genre_from_cache(elastic, client, genre_es, genre_dto):
    """Данные о жанре должны сохраняться в кэше после запроса в основную БД."""
    new_name = "GGG"
    body = genre_dto.dict()
    body["name"] = new_name

    from_source = await client.get(f"/api/v1/genres/{genre_dto.uuid}")
    assert from_source["name"] == genre_dto.name

    await elastic.index(index="genre", doc_type="_doc", id=str(genre_dto.uuid), body=body, refresh="wait_for")
    from_cache = await client.get(f"/api/v1/genres/{genre_dto.uuid}")
    assert from_cache["name"] != new_name
    assert from_cache["name"] == genre_dto.name
