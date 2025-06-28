import sys
import os
import pathlib
from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, Any, List, Optional


project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(str(project_root))

app = FastAPI(title="TeamUp API")


from services.redis_service import RedisService
redis_service = RedisService()

def validate_username(username: str):
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")
    return username



@app.get("/neo4j/user_exists/{username}")
async def user_exists(username: str = Depends(validate_username)):
    """Check if a user exists."""
    # In future, this will hit Neo4j or MongoDB
    # For now, just pretend it works
    return {"exists": True}


@app.get("/neo4j/get_user/{username}")
async def get_user(username: str = Depends(validate_username)):
    """Get full user details."""
    status = redis_service.get_availability(username)
    return {
        "username": username,
        "availability": status or "offline"
    }


@app.post("/neo4j/add_user")
async def add_user(user_data: Dict[str, Any]):
    """Add a new user."""
    username = user_data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    return {"message": "User added successfully"}


@app.put("/neo4j/update_availability")
async def update_availability(username: str, status: str):
    """Update user availability."""
    valid_statuses = ["online", "busy", "offline", "available"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    success = redis_service.set_availability(username, status)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update Redis")

    return {"message": "Availability updated", "status": status}


@app.post("/neo4j/find_matches")
async def find_matches(criteria: Dict[str, Any]):
    """Find matching users based on criteria."""
    role = criteria.get("role")
    skills = criteria.get("skills", [])
    min_experience = criteria.get("min_experience", 0)

    matches = [
        {
            "username": f"user{i}",
            "role": role,
            "skills": skills,
            "experience": min_experience + i
        } for i in range(1, 4)
    ]
    return {"matches": matches}


@app.get("/neo4j/contact/{username}")
async def get_contact(username: str = Depends(validate_username)):
    """Get contact info (email, phone)."""
    return {"email": f"{username}@example.com", "phone": "+1234567890"}


@app.get("/neo4j/similar_users/{username}")
async def similar_users(username: str = Depends(validate_username)):
    """Find users with overlapping interests."""
 
    return {
        "similar_users": [
            {
                "name": "Similar User 1",
                "common_interests": ["AI", "Data Science"],
                "email": "similar1@example.com",
                "phone": "+0987654321"
            },
            {
                "name": "Similar User 2",
                "common_interests": ["Machine Learning"],
                "email": "similar2@example.com",
                "phone": "+1122334455"
            }
        ]
    }



@app.put("/availability/{user_id}")
async def manage_user_availability(user_id: str, status: str = None):
    """Set or get user availability status."""
    if status:
        valid_statuses = ["online", "busy", "offline", "available"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        success = redis_service.set_availability(user_id, status)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set availability")
        return {"user_id": user_id, "availability": status}

    status = redis_service.get_availability(user_id)
    if status:
        return {"user_id": user_id, "availability": status}

    return {"user_id": user_id, "availability": "offline"}


@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str) -> Dict[str, Any]:
    """Get cached or fresh recommendations."""
    cached = redis_service.get_cached_recommendation(user_id)
    if cached:
        return {"matches": cached}

    matches = [
        {
            "username": f"match_{i}",
            "role": "developer",
            "skills": ["Python", "FastAPI"],
            "experience": 3
        } for i in range(1, 4)
    ]
    redis_service.cache_recommendation(user_id, matches)
    return {"matches": matches}