from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from common.constants import DEFAULT_PAGE_SIZE
from common.exceptions import NotFoundError
from repositories.films import FilmRepository, get_film_repository
from schemas.films import FilmDetail, FilmList


router = APIRouter()


@router.get("/", response_model=list[FilmList], summary="Фильмы")
async def get_films(
    sort: str | None = None,
    genre: str | None = None,
    page_size: int | None = DEFAULT_PAGE_SIZE,
    page_number: int | None = 0,
    film_repository: FilmRepository = Depends(get_film_repository),
):
    """Получение списка фильмов.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/films?sort=imdb_rating:desc`.
    """
    films = await film_repository.get_all_films(page_size=page_size, page_number=page_number, genre=genre, sort=sort)
    return films


@router.get("/search", response_model=list[FilmList], summary="Поиск по фильмам")
async def search_films(
    query: str,
    sort: str | None = None,
    page_size: int | None = DEFAULT_PAGE_SIZE,
    page_number: int | None = 0,
    film_repository: FilmRepository = Depends(get_film_repository),
):
    """Поиск по фильмам.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/films?sort=imdb_rating:desc`.
    """
    films = await film_repository.search_films(page_size=page_size, page_number=page_number, query=query, sort=sort)
    return films


@router.get("/{uuid}", response_model=FilmDetail, summary="Фильм")
async def get_film(uuid: UUID, film_repository: FilmRepository = Depends(get_film_repository)):
    """Получение фильма по `uuid`."""
    try:
        film = await film_repository.get_film_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="film not found")

    return film
