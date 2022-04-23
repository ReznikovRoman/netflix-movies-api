from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import PageNumberPaginationQueryParams, SortQueryParams
from common.exceptions import NotFoundError
from repositories.persons import PersonRepository, get_person_repository
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail


router = APIRouter()


@router.get("/", response_model=list[PersonList], summary="Персоны")
async def get_persons(
    person_repository: PersonRepository = Depends(get_person_repository),
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
):
    """Получения списка персон (с возможной фильтрацией, пагинацией и сортировкой)."""
    persons = await person_repository.get_persons(
        page_size=pagination_params.page_size, page_number=pagination_params.page_number, sort=sort_params.sort,
    )
    return persons


@router.get("/search", response_model=list[PersonShortDetail], summary="Поиск по персонам")
async def search_persons(
    person_repository: PersonRepository = Depends(get_person_repository),
    sort_params: SortQueryParams = Depends(SortQueryParams),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Поиск по Персонам.", required=True),
):
    """Поиск по персонам.

    Сортировка `sort`: https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html.

    Пример: `GET /api/v1/persons/search?sort=-full_name`.
    """
    persons = await person_repository.search_persons(
        page_size=pagination_params.page_size, page_number=pagination_params.page_number, sort=sort_params.sort,
        query=query,
    )
    return persons


@router.get("/{uuid}", response_model=PersonShortDetail, summary="Персона")
async def get_person(uuid: UUID, person_repository: PersonRepository = Depends(get_person_repository)):
    """Получение персоны по `uuid` c простым списком id его фильмов."""
    try:
        person = await person_repository.get_person_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="person not found")

    return person


@router.get("/full/{uuid}", response_model=PersonFullDetail, summary="Персона по ролям")
async def get_person_full(uuid: UUID, person_repository: PersonRepository = Depends(get_person_repository)):
    """Получение персоны c списком фильмов по `uuid` с разбивкой по ролям."""
    try:
        person = await person_repository.get_person_detail_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="person not found")
    return person


@router.get("/{uuid}/films", response_model=list[FilmList], summary="Фильмы Персоны")
async def get_person_films(uuid: UUID, person_repository: PersonRepository = Depends(get_person_repository)):
    try:
        film_list = await person_repository.get_films_of_person(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="person not found")
    return film_list
