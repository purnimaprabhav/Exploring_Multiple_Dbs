import os
from dotenv import load_dotenv
from redis import Redis
from typing import Optional

load_dotenv()

import redis

_redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            # db=os.getenv("REDIS_DB"),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True,
            username=os.getenv("REDIS_USERNAME")
        )
    return _redis_client



