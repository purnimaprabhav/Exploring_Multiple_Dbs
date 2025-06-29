import aioredis
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

async def get_redis():
    return await aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        db=REDIS_DB,
        decode_responses=True
    )