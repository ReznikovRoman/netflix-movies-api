from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, Query, Request

from movies.api.deps import PageNumberPaginationQueryParams
from movies.containers import Container
from movies.domain.films import FilmList
from movies.domain.persons.repositories import PersonRepository
from movies.domain.persons.schemas import PersonList, PersonShortDetail
from movies.domain.roles import PersonFullDetail

router = APIRouter(tags=["Persons"])


@router.get("/", response_model=list[PersonList], summary="Персоны")
@inject
async def get_persons(
    request: Request,
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение списка персон."""
    return await person_repository.get_all(
        url=request.url.query, page_size=pagination_params.page_size, page_number=pagination_params.page_number)


@router.get("/search", response_model=list[PersonShortDetail], summary="Поиск по персонам")
@inject
async def search_persons(
    request: Request,
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Поиск по Персонам.", required=True),
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Поиск по персонам."""
    return await person_repository.search(
        query=query, url=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number,
    )


@router.get("/{uuid}", response_model=PersonShortDetail, summary="Персона")
@inject
async def get_person(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение персоны по `uuid` без разбиения фильмов по ролям."""
    return await person_repository.get_by_id(uuid)


@router.get("/full/{uuid}", response_model=PersonFullDetail, summary="Персона [с ролями]")
@inject
async def get_person_detailed(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение персоны по `uuid` с разбиением фильмов по ролям."""
    return await person_repository.get_by_id_detailed(uuid)


@router.get("/{uuid}/films", response_model=list[FilmList], summary="Фильмы персоны")
@inject
async def get_person_films(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Получение фильмов персоны по её `uuid`."""
    return await person_repository.get_person_films(uuid)
