from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from common.exceptions import NotFoundError
from repositories.films import FilmRepository, get_film_repository
from schemas.films import FilmDetail


router = APIRouter()


@router.get("/{uuid}", response_model=FilmDetail)
async def get_all_films(uuid: UUID, film_repository: FilmRepository = Depends(get_film_repository)):
    """Получение списка фильмов."""
    try:
        film = await film_repository.get_film_by_id(uuid)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="film not found")

    return film
