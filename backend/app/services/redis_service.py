import json
from typing import Any, List, Optional, Union
from redis import Redis
from backend.app.config.db.redis_conn import get_redis_client


async def get_cached_data(key: str) -> Optional[Any]:
    redis_client = get_redis_client()
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached_data(key: str, data: Any, expiration_seconds: int = 3600) -> bool:
    redis_client = get_redis_client()
    serialized_data = json.dumps(data)
    return redis_client.setex(key, expiration_seconds, serialized_data)


async def delete_cached_data(key: str) -> bool:
    redis_client = get_redis_client()
    return redis_client.delete(key) > 0


async def clear_cache_pattern(pattern: str) -> int:
    redis_client = get_redis_client()
    keys = redis_client.keys(pattern)
    if keys:
        return redis_client.delete(*keys)
    return 0


async def set_user_availability(username: str, available: bool):
    return await set_cached_data(f"availability:{username}", {"available": available}, 3600)


async def get_user_availability(username: str) -> Optional[bool]:
    data = await get_cached_data(f"availability:{username}")
    return data["available"] if data else None


async def clear_user_availability(username: str):
    return await delete_cached_data(f"availability:{username}")


async def cache_recommendations(username: str, recommendations: List[str], expiration_seconds: int = 1800):
    return await set_cached_data(f"recommendation:{username}", recommendations, expiration_seconds)


async def get_cached_recommendations(username: str) -> Optional[List[str]]:
    return await get_cached_data(f"recommendation:{username}")


async def clear_recommendations(username: str):
    return await delete_cached_data(f"recommendation:{username}")