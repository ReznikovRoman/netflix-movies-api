from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from common.exceptions import NotFoundError
from schemas.genres import GenreDetail
from services.genres import GenreService, get_genre_service


router = APIRouter()


@router.get("/{uuid}", response_model=GenreDetail, summary="Жанр")
async def get_genre(uuid: UUID, genre_service: GenreService = Depends(get_genre_service)):
    """Получение жанра по `uuid`."""
    try:
        genre = await genre_service.get_genre_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="genre not found")
    return genre


@router.get("/", response_model=list[GenreDetail], summary="Жанры")
async def get_genres(genre_service: GenreService = Depends(get_genre_service)):
    """Получения списка жанров."""
    genres = await genre_service.get_all_genres()
    return genres
