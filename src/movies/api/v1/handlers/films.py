from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, Query, Request

from movies.api.deps import PageNumberPaginationQueryParams, SortQueryParams, get_user_roles
from movies.containers import Container
from movies.domain.films import FilmDetail, FilmList, FilmRepository
from movies.domain.users import UserService

router = APIRouter(tags=["Films"])


@router.get("/", response_model=list[FilmList], summary="Films")
@inject
async def get_films(
    request: Request,
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    genre: str | None = Query(default=None, alias="filter[genre]", description="Genre filter."),
    user_roles: list[str] = Depends(get_user_roles),
    film_repository: FilmRepository = Depends(Provide[Container.film_repository]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """Get list of films.

    Return all films if user has a subscription, only public ones otherwise.

    Sorting `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Example: `GET /api/v1/films?sort=-imdb_rating`.
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


@router.get("/search", response_model=list[FilmList], summary="Films search")
@inject
async def search_films(
    request: Request,
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Search query.", required=True),
    film_repository: FilmRepository = Depends(Provide[Container.film_repository]),
):
    """Films search.

    Sorting `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Example: `GET /api/v1/films/search?sort=-imdb_rating`.
    """
    return await film_repository.search(
        query=query, url=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number, sort=sort_params.sort,
    )


@router.get("/{uuid}", response_model=FilmDetail, summary="Film")
@inject
async def get_film(
    uuid: UUID,
    film_repository: FilmRepository = Depends(Provide[Container.film_repository]),
):
    """Get film detail by id."""
    raise Exception()
    return await film_repository.get_by_id(uuid)
