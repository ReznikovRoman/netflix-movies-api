from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends

from movies.containers import Container
from movies.domain.genres import GenreDetail, GenreRepository

router = APIRouter(tags=["Genres"])


@router.get("/{uuid}", response_model=GenreDetail, summary="Genre")
@inject
async def get_genre(
    uuid: UUID,
    genre_repository: GenreRepository = Depends(Provide[Container.genre_repository]),
):
    """Get genre detail by id."""
    return await genre_repository.get_by_id(uuid)


@router.get("/", response_model=list[GenreDetail], summary="Genres")
@inject
async def get_genres(genre_repository: GenreRepository = Depends(Provide[Container.genre_repository])):
    """Get list of genres."""
    return await genre_repository.get_list()
