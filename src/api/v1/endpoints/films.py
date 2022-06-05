from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.constants import MESSAGE
from api.deps import PageNumberPaginationQueryParams, SortQueryParams, get_user_roles
from common.exceptions import NotFoundError
from containers import Container
from repositories.films import FilmRepository
from schemas.films import FilmDetail, FilmList
from services.users import UserService


router = APIRouter()


@router.get("/", response_model=list[FilmList], summary="Фильмы")
@inject
async def get_films(
    request: Request,
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    genre: str | None = Query(default=None, alias="filter[genre]", description="Сортировка по жанрам."),
    user_roles: list[str] = Depends(get_user_roles),
    film_repository: FilmRepository = Depends(Provide[Container.film_repository]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """Получение списка фильмов.

    Если у пользователя есть подписка - показываем все фильмы, если нет - то только публичные/открытые.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/films?sort=-imdb_rating`.
    """
    is_subscriber = user_service.is_subscriber(user_roles)
    params = {
        "url": request.url.query,
        "page_size": pagination_params.page_size, "page_number": pagination_params.page_number,
        "sort": sort_params.sort,
        "genre": genre,
    }
    if is_subscriber:
        return await film_repository.get_all(**params)
    return await film_repository.get_public(**params)


@router.get("/search", response_model=list[FilmList], summary="Поиск по фильмам")
@inject
async def search_films(
    request: Request,
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Поиск по Фильмам.", required=True),
    film_repository: FilmRepository = Depends(Provide[Container.film_repository]),
):
    """Поиск по фильмам.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/films/search?sort=-imdb_rating`.
    """
    films = await film_repository.search(
        query=query, url=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number, sort=sort_params.sort,
    )
    return films


@router.get("/{uuid}", response_model=FilmDetail, summary="Фильм")
@inject
async def get_film(
    uuid: UUID,
    film_repository: FilmRepository = Depends(Provide[Container.film_repository]),
):
    """Получение фильма по `uuid`."""
    try:
        film = await film_repository.get_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.FILM_NOT_FOUND.value)
    return film
