# backend/app/services/redis_service.py
import json
from typing import Any, Optional, Union
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