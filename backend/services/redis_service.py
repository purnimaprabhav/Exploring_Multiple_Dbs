import json
from typing import Optional, Dict, Any
from core.redis_client import get_redis

class RedisService:
    def __init__(self):
        self.client = None

    async def initialize(self):
        self.client = await get_redis()

    async def set_availability(self, user_id: str, status: str) -> bool:
        try:
            await self.client.set(f"teamup:availability:{user_id}", status, ex=3600)
            return True
        except Exception as e:
            print(f"[Redis] Error setting availability for {user_id}: {e}")
            return False

    async def get_availability(self, user_id: str) -> Optional[str]:
        try:
            return await self.client.get(f"teamup:availability:{user_id}")
        except Exception as e:
            print(f"[Redis] Error getting availability for {user_id}: {e}")
            return None

    async def cache_recommendation(self, user_id: str, recommendations: Dict[str, Any]) -> bool:
        try:
            await self.client.set(
                f"teamup:recommendation:{user_id}",
                json.dumps(recommendations),
                ex=1800
            )
            return True
        except Exception as e:
            print(f"[Redis] Error caching recommendation for {user_id}: {e}")
            return False
    def get_cached_recommendation(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            data = redis_client.get(f"teamup:recommendation:{user_id}")  # Use consistent key prefix
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"[Redis] Error retrieving cached recommendation for {user_id}: {e}")
            return None