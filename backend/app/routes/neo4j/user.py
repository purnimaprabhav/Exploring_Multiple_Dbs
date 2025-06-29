from fastapi import APIRouter, HTTPException
from backend.app.services import neo4j_service
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/neo4j")

@router.get("/user_exists/{username}")
def user_exists(username: str):
    exists = neo4j_service.check_user_exists(username)
    return {"exists": exists}

@router.get("/get_user/{username}")
def get_user(username: str):
    user = neo4j_service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

class UserCreate(BaseModel):
    username: str
    name: str
    number: str
    email: str
    role: str
    skills: List[str]
    experience: int
    interests: List[str]
    organization: str
    availability: bool

@router.post("/add_user")
def add_user(user: UserCreate):
    result = neo4j_service.create_user(user)
    return {"message": "User created", "success": result}

class AvailabilityUpdate(BaseModel):
    username: str
    availability: bool

@router.put("/update_availability")
def update_user_availability(data: AvailabilityUpdate):
    success = neo4j_service.update_availability(data.username, data.availability)
    if success:
        return {"message": "Availability updated successfully"}
    else:
        return {"message": "User not found"}

@router.post("/find_matches")
def find_matches(payload: dict):
    try:
        result = neo4j_service.find_matching_users(
            payload.get("role"), payload.get("skills", []), payload.get("min_experience", 0)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contact/{username}")
def get_user_contact(username: str):
    try:
        contact = neo4j_service.get_contact(username)
        if not contact:
            raise HTTPException(status_code=404, detail="User not found")
        return contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
