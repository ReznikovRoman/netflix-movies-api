from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends

from movies.containers import Container
from movies.repositories.genres import GenreRepository
from movies.schemas.genres import GenreDetail

router = APIRouter(tags=["Genres"])


@router.get("/{uuid}", response_model=GenreDetail, summary="Жанр")
@inject
async def get_genre(
    uuid: UUID,
    genre_repository: GenreRepository = Depends(Provide[Container.genre_repository]),
):
    """Получение жанра по `uuid`."""
    return await genre_repository.get_by_id(uuid)


@router.get("/", response_model=list[GenreDetail], summary="Жанры")
@inject
async def get_genres(genre_repository: GenreRepository = Depends(Provide[Container.genre_repository])):
    """Получения списка жанров."""
    return await genre_repository.get_list()
