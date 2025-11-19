from fastapi import APIRouter
from services.ms2 import get_movie_from_ms2

router = APIRouter()

@router.get("/movies/{movie_id}")
async def composite_get_movie(movie_id: str):
    result = await get_movie_from_ms2(movie_id)
    return {"source": "composite", "data": result}
