import redis
import json
from typing import Optional, Dict, Any, Set
from dotenv import load_dotenv
import os

load_dotenv()

class RedisService:
    def __init__(self):
        """Initialize Redis client."""
        try:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
            self.client.ping()
        except redis.ConnectionError as e:
            raise Exception(f"Failed to connect to Redis: {e}")

    def set_availability(self, user_id: str, status: str) -> bool:
        """Set user availability status with 1-hour expiry."""
        try:
            self.client.set(f"availability:{user_id}", status, ex=3600)
            return True
        except redis.RedisError as e:
            print(f"Error setting availability for user {user_id}: {e}")
            return False

    def get_availability(self, user_id: str) -> Optional[str]:
        """Get user availability status from cache."""
        try:
            return self.client.get(f"availability:{user_id}")
        except redis.RedisError as e:
            print(f"Error getting availability for user {user_id}: {e}")
            return None

    def cache_recommendation(self, user_id: str, recommendations: Dict[str, Any]) -> bool:
        """Cache recommendation results for 30 minutes."""
        try:
            self.client.set(
                f"recommendation:{user_id}",
                json.dumps(recommendations),
                ex=1800
            )
            return True
        except redis.RedisError as e:
            print(f"Error caching recommendation for user {user_id}: {e}")
            return False

    def get_cached_recommendation(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached recommendation data."""
        try:
            data = self.client.get(f"recommendation:{user_id}")
            if data:
                return json.loads(data)
            return None
        except redis.RedisError as e:
            print(f"Error retrieving cached recommendation for user {user_id}: {e}")
            return None

    def clear_user_cache(self, user_id: str) -> bool:
        """Clear all cached data for a user."""
        try:
            self.client.delete(f"availability:{user_id}")
            self.client.delete(f"recommendation:{user_id}")
            self.client.srem("online_users", user_id)
            return True
        except redis.RedisError as e:
            print(f"Error clearing cache for user {user_id}: {e}")
            return False

    def add_online_user(self, user_id: str) -> bool:
        """Add a user to the online users set."""
        try:
            self.client.sadd("online_users", user_id)
            self.client.expire("online_users", 3600)
            return True
        except redis.RedisError as e:
            print(f"Error adding online user {user_id}: {e}")
            return False

    def get_online_users(self) -> Set[str]:
        """Get all currently online users."""
        try:
            return self.client.smembers("online_users") or set()
        except redis.RedisError as e:
            print(f"Error getting online users: {e}")
            return set()
