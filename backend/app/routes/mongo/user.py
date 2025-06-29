from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import List, Optional
from pydantic import BaseModel
from backend.app.services.mongodb_service import get_all_users
from backend.app.config.db.mongo_conn import get_mongo_db
from backend.app.models.user import UserCreate, UserLogin, AvailabilityUpdate
from backend.app.services.redis_service import get_cached_data, set_cached_data, delete_cached_data

router = APIRouter(prefix="/mongo")

@router.get("/getallusers")
async def read_all_users(db = Depends(get_mongo_db)):
    cache_key = "mongo:all_users"
    cached_users = await get_cached_data(cache_key)

    if cached_users:
        return cached_users

    users = await get_all_users(db)
    await set_cached_data(cache_key, users, 300)
    return users


@router.post("/signup", status_code=201, response_model=dict)
async def signup(user: UserCreate, db = Depends(get_mongo_db)):
    user = user.dict()
    try:
        result = await db["users"].insert_one(user)
        await delete_cached_data("mongo:all_users")
        await clear_cache_pattern("mongo:filter_users:*")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_id": str(result.inserted_id),
        "message": "User created successfully",
    }


@router.post("/login", response_model=dict)
async def login(user: UserLogin, db = Depends(get_mongo_db)):
    user = user.dict()
    try:
        check_user = await db["users"].find_one({"username": user["username"]}, {"_id": 0})
        if not check_user:
            return {"message": "Login failed", "user": None}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Login successful", "user": check_user}

@router.put("/editProfile", response_model=dict, status_code=200, description="Update user profile.")
async def update_user_profile(data: UserCreate, db=Depends(get_mongo_db)):
    payload = data.dict()
    username = payload.pop("username")

    result = await db["users"].update_one(
        {"username": username},
        {"$set": payload}
    )

    if result.matched_count == 0:
        # No user with that username
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )

    updated_user = await db["users"].find_one(
        {"username": username},
        {"_id": 0}
    )

    return {
        "message": "Profile updated successfully",
        "user": updated_user
    }


@router.put("/toggleAvailability", response_model=dict, status_code=200, description="Update user availability.")
async def update_user_availability(data: AvailabilityUpdate, db=Depends(get_mongo_db)):
    updateUserAvail = await db["users"].update_one(
        {"username": data.username},
        {"$set": {"availability": data.availability}}
    )

    if updateUserAvail.matched_count == 0:
        return {"message": "User not found"}

    return {"message": "Availability updated successfully"}


@router.get(
    "/filterUsers",
    # response_model=List[UserResponse],
    summary="List users with optional filtering",
)
async def list_users(
    role: Optional[str] = Query(None),
    availability: Optional[bool] = Query(None),
    skill: Optional[str] = Query(None),
    experience_min: Optional[int] = Query(None, ge=0),
    interest: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db = Depends(get_mongo_db),
):

    cache_key = f"mongo:filter_users:{role}:{availability}:{skill}:{experience_min}:{interest}:{skip}:{limit}"
    cached_results = await get_cached_data(cache_key)
    if cached_results:
        return cached_results

    filt: dict = {}
    if role is not None:
        filt["role"] = role
    if availability is not None:
        filt["availability"] = availability
    if skill is not None:
        filt["skills"] = skill
    if interest is not None:
        filt["interests"] = interest
    if experience_min is not None:
        filt["experience"] = {"$gte": experience_min}

    cursor = db["users"].find(filt).skip(skip).limit(limit)

    docs = await cursor.to_list(length=limit)
    for doc in docs:
        doc["_id"] = str(doc["_id"])

    await set_cached_data(cache_key, docs, 120)
    return docs