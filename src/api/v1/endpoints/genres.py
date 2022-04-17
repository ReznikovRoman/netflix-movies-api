from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from common.exceptions import NotFoundError
from repositories.genres import GenreRepository, get_genre_repository
from schemas.genres import GenreDetail


router = APIRouter()


@router.get("/{uuid}", response_model=GenreDetail, summary="Жанр")
async def get_genre(uuid: UUID, genre_repository: GenreRepository = Depends(get_genre_repository)):
    """Получение жанра по `uuid`."""
    try:
        genre = await genre_repository.get_genre_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="genre not found")

    return genre


@router.get("/", response_model=list[GenreDetail], summary="Жанры")
async def get_genres(genre_repository: GenreRepository = Depends(get_genre_repository)):
    """Получения списка жанров."""
    genres = await genre_repository.get_all_genres()
    return genres
