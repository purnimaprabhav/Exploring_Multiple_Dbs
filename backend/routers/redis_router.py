from fastapi import APIRouter, Depends, HTTPException
from services.redis_service import RedisService
from pydantic import BaseModel

router = APIRouter(prefix="/redis", tags=["Redis"])

async def get_redis_service() -> RedisService:
    return RedisService()

class AvailabilityUpdate(BaseModel):
    status: str

@router.put("/availability/{user_id}")
async def update_user_availability(
    user_id: str,
    payload: AvailabilityUpdate,
    service: RedisService = Depends(get_redis_service)
):
    success = await service.set_availability(user_id, payload.status)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update availability")
    return {"message": "Availability updated", "status": payload.status}

@router.get("/availability/{user_id}")
async def get_user_availability(
    user_id: str,
    service: RedisService = Depends(get_redis_service)
):
    status = await service.get_availability(user_id)
    return {"user_id": user_id, "status": status or "offline"}