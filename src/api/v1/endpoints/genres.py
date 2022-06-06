from uuid import UUID

from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends

from containers import Container
from repositories.genres import GenreRepository
from schemas.genres import GenreDetail


router = APIRouter()


@router.get("/{uuid}", response_model=GenreDetail, summary="Жанр")
@inject
async def get_genre(
    uuid: UUID,
    genre_repository: GenreRepository = Depends(Provide[Container.genre_repository]),
):
    """Получение жанра по `uuid`."""
    genre = await genre_repository.get_by_id(uuid)
    return genre


@router.get("/", response_model=list[GenreDetail], summary="Жанры")
@inject
async def get_genres(genre_repository: GenreRepository = Depends(Provide[Container.genre_repository])):
    """Получения списка жанров."""
    genres = await genre_repository.get_list()
    return genres
