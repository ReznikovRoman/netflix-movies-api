from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.constants import MESSAGE
from api.deps import PageNumberPaginationQueryParams
from common.exceptions import NotFoundError
from containers import Container
from repositories.persons import PersonRepository
from schemas.films import FilmList
from schemas.persons import PersonList, PersonShortDetail
from schemas.roles import PersonFullDetail


router = APIRouter()


@router.get("/", response_model=list[PersonList], summary="Персоны")
@inject
async def get_persons(
    request: Request,
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение списка персон."""
    persons = await person_repository.get_all(
        url=request.url.query, page_size=pagination_params.page_size, page_number=pagination_params.page_number)
    return persons


@router.get("/search", response_model=list[PersonShortDetail], summary="Поиск по персонам")
@inject
async def search_persons(
    request: Request,
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Поиск по Персонам.", required=True),
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Поиск по персонам."""
    persons = await person_repository.search(
        query=query, url=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number,
    )
    return persons


@router.get("/{uuid}", response_model=PersonShortDetail, summary="Персона")
@inject
async def get_person(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение персоны по `uuid` без разбиения фильмов по ролям."""
    try:
        person = await person_repository.get_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.PERSON_NOT_FOUND.value)
    return person


@router.get("/full/{uuid}", response_model=PersonFullDetail, summary="Персона [с ролями]")
@inject
async def get_person_detailed(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение персоны по `uuid` с разбиением фильмов по ролям."""
    try:
        person = await person_repository.get_by_id_detailed(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.PERSON_NOT_FOUND.value)
    return person


@router.get("/{uuid}/films", response_model=list[FilmList], summary="Фильмы персоны")
@inject
async def get_person_films(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение фильмов персоны по её `uuid`."""
    try:
        person_films = await person_repository.get_person_films(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGE.PERSON_NOT_FOUND.value)
    return person_films
