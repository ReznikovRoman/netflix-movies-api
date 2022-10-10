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


@router.get("/", response_model=list[PersonList], summary="Persons")
@inject
async def get_persons(
    request: Request,
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Get list of persons."""
    return await person_repository.get_all(
        url=request.url.query, page_size=pagination_params.page_size, page_number=pagination_params.page_number)


@router.get("/search", response_model=list[PersonShortDetail], summary="Persons search")
@inject
async def search_persons(
    request: Request,
    pagination_params: PageNumberPaginationQueryParams = Depends(PageNumberPaginationQueryParams),
    query: str = Query(..., description="Search query.", required=True),
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Persons search."""
    return await person_repository.search(
        query=query, url=request.url.query,
        page_size=pagination_params.page_size, page_number=pagination_params.page_number,
    )


@router.get("/{uuid}", response_model=PersonShortDetail, summary="Person")
@inject
async def get_person(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Get person short details by id."""
    return await person_repository.get_by_id(uuid)


@router.get("/full/{uuid}", response_model=PersonFullDetail, summary="Person [with roles]")
@inject
async def get_person_detailed(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Get person full details (with roles included) by id."""
    return await person_repository.get_by_id_detailed(uuid)


@router.get("/{uuid}/films", response_model=list[FilmList], summary="Person films")
@inject
async def get_person_films(
    uuid: UUID,
    person_repository: PersonRepository = Depends(Provide[Container.person_repository]),
):
    """Get person films by id."""
    return await person_repository.get_person_films(uuid)
