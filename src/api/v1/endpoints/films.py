from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.constants import MESSAGE
from api.deps import PageNumberPaginationQueryParams, SortQueryParams, get_user_roles
from common.constants import DefaultRoles
from common.exceptions import NotFoundError
from schemas.films import FilmDetail, FilmList
from services.films import FilmService, get_film_service


router = APIRouter()


@router.get("/", response_model=list[FilmList], summary="Фильмы")
async def get_films(
    request: Request,
    user_roles: list[str] = Depends(get_user_roles),
    film_service: FilmService = Depends(get_film_service),
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    genre: str | None = Query(default=None, alias="filter[genre]", description="Сортировка по жанрам."),
):
    """Получение списка фильмов.

    Если у пользователя есть подписка - показываем все фильмы, если нет - то только публичные/открытые.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/films?sort=-imdb_rating`.
    """
    has_subscription = DefaultRoles.SUBSCRIBERS.value in user_roles
    params = {
        "request_params": request.url.query,
        "page_size": pagination_params.page_size, "page_number": pagination_params.page_number,
        "sort": sort_params.sort,
        "genre": genre,
    }
    if has_subscription:
        return await film_service.get_all_films(**params)
    return await film_service.get_public_films(**params)


@router.get("/search", response_model=list[FilmList], summary="Поиск по фильмам")
async def search_films(
    request: Request,
    film_service: FilmService = Depends(get_film_service),
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Поиск по Фильмам.", required=True),
):
    """Поиск по фильмам.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/films/search?sort=-imdb_rating`.
    """
    films = await film_service.search_films(
        request_params=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number, sort=sort_params.sort,
        query=query,
    )
    return films


@router.get("/{uuid}", response_model=FilmDetail, summary="Фильм")
async def get_film(uuid: UUID, film_service: FilmService = Depends(get_film_service)):
    """Получение фильма по `uuid`."""
    try:
        film = await film_service.get_film_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.FILM_NOT_FOUND.value)
    return film
