from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, Query, Request

from api.deps import PageNumberPaginationQueryParams
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
    person = await person_repository.get_by_id(uuid)
    return person


@router.get("/full/{uuid}", response_model=PersonFullDetail, summary="Персона [с ролями]")
@inject
async def get_person_detailed(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение персоны по `uuid` с разбиением фильмов по ролям."""
    person = await person_repository.get_by_id_detailed(uuid)
    return person


@router.get("/{uuid}/films", response_model=list[FilmList], summary="Фильмы персоны")
@inject
async def get_person_films(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение фильмов персоны по её `uuid`."""
    person_films = await person_repository.get_person_films(uuid)
    return person_films
