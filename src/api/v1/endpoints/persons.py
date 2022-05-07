from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.constants import MESSAGE
from api.deps import PageNumberPaginationQueryParams
from common.exceptions import NotFoundError
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail
from services.persons import PersonService, get_person_service


router = APIRouter()


@router.get("/", response_model=list[PersonList], summary="Персоны")
async def get_persons(
    request: Request,
    person_service: PersonService = Depends(get_person_service),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
):
    """Получение списка персон."""
    persons = await person_service.get_all_persons(
        request_params=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number,
    )
    return persons


@router.get("/search", response_model=list[PersonShortDetail], summary="Поиск по персонам")
async def search_persons(
    request: Request,
    person_service: PersonService = Depends(get_person_service),
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Поиск по Персонам.", required=True),
):
    """Поиск по персонам."""
    persons = await person_service.search_persons(
        request_params=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number, query=query,
    )
    return persons


@router.get("/{uuid}", response_model=PersonShortDetail, summary="Персона")
async def get_person(uuid: UUID, person_service: PersonService = Depends(get_person_service)):
    """Получение персоны по `uuid` без разбиения фильмов по ролям."""
    try:
        person = await person_service.get_person_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.PERSON_NOT_FOUND.value)

    return person


@router.get("/full/{uuid}", response_model=PersonFullDetail, summary="Персона [с ролями]")
async def get_person_full(uuid: UUID, person_service: PersonService = Depends(get_person_service)):
    """Получение персоны по `uuid` с разбиением фильмов по ролям."""
    try:
        person = await person_service.get_person_detail_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.PERSON_NOT_FOUND.value)

    return person


@router.get("/{uuid}/films", response_model=list[FilmList], summary="Фильмы персоны")
async def get_person_films(uuid: UUID, person_service: PersonService = Depends(get_person_service)):
    """Получение фильмов персоны по её `uuid`."""
    try:
        person_films = await person_service.get_person_films(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.PERSON_NOT_FOUND.value)

    return person_films
