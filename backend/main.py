import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from fastapi import FastAPI, HTTPException
from backend.app.api import neo4j_api
from backend.services.redis_service import RedisService
from typing import Dict, Any, Set
from backend.app.api.neo4j_api import neo4j_service

app = FastAPI(title="TeamUp API")
redis_service = RedisService()
app.include_router(neo4j_api.router)

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
        
        # Sync with Neo4j
        neo4j_availability = status in ["online", "available"]
        neo4j_service.update_availability(user_id, neo4j_availability)

        # Track online status
        if status in ["online", "available"]:
            redis_service.add_online_user(user_id)


        return {"user_id": user_id, "availability": status}

    status = redis_service.get_availability(user_id)
    if status:
        return {"user_id": user_id, "availability": status}

    user = neo4j_service.get_user_by_username(user_id)
    if user and "availability" in user:
        status = "available" if user["availability"] else "offline"
        redis_service.set_availability(user_id, status)
        return {"user_id": user_id, "availability": status}

    status = "offline"  # Final fallback
    redis_service.set_availability(user_id, status)
    return {"user_id": user_id, "availability": status}

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str) -> Dict[str, Any]:
    """Get cached or fresh recommendations for a user."""
    cached = redis_service.get_cached_recommendation(user_id)
    if cached:
        return {"matches": cached}

    user = neo4j_service.get_user_by_username(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    neo4j_recommendations = neo4j_service.find_matching_users(
        role=user.get("role", ""),
        skills=user.get("skills", []),
        min_exp=user.get("experience", 0)
    )
    redis_service.cache_recommendation(user_id, neo4j_recommendations)
    return {"matches": neo4j_recommendations}

@app.get("/online-users")
async def get_online_users() -> Set[str]:
    """Get all users currently online."""
    return redis_service.get_online_users()
