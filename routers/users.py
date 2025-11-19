from fastapi import APIRouter
from services.ms1 import get_user_from_ms1

router = APIRouter()

@router.get("/users/{user_id}")
async def composite_get_user(user_id: str):
    # eventually call MS1
    result = await get_user_from_ms1(user_id)
    return {"source": "composite", "data": result}
