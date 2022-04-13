from fastapi import APIRouter

from schemas.messages import Message


router = APIRouter()


@router.get("/", response_model=Message)
async def homepage():
    """Главная страница."""
    return {"message": "Netflix API"}
