from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from schemas.films import FilmDetail
from schemas.genres import GenreDetail


if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch


def find_object_by_value(objects: Sequence, key: str, value: Any) -> object:
    """Поиск объекта в списке `objects` по ключу `key` со значением `value`."""
    _filter = filter(lambda obj: getattr(obj, key) == value, objects)
    return next(_filter)


async def add_film_document_to_elastic(elastic: AsyncElasticsearch, film: FilmDetail) -> None:
    body = film.dict()
    body["genres_names"] = [genre.name for genre in film.genre]
    body["actors_names"] = [actor.full_name for actor in film.actors]
    body["writers_names"] = [writer.full_name for writer in film.writers]
    body["directors_names"] = [director.full_name for director in film.directors]
    await elastic.index(index="movies", doc_type="_doc", id=film.uuid, body=body, refresh="wait_for")


async def add_genre_document_to_elastic(elastic: AsyncElasticsearch, genre: GenreDetail) -> None:
    body = genre.dict()
    await elastic.index(index="genre", doc_type="_doc", id=genre.uuid, body=body, refresh="wait_for")
