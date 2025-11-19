from fastapi import APIRouter
from services.ms3 import create_review_in_ms3

router = APIRouter()

@router.post("/reviews")
async def composite_create_review(review: dict):
    result = await create_review_in_ms3(review)
    return {"source": "composite", "data": result}
