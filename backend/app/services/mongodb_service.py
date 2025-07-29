import asyncio


async def get_all_users(db):
    cursor = db["users"].find({}, {"_id": 0})
    users = await cursor.to_list(length=1000)
    return users