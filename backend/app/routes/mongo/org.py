from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from backend.app.config.db.mongo_conn import get_mongo_db
from backend.app.models.org import OrgCreate, AddMember

router = APIRouter(prefix="/mongo")


@router.post(
    "/createNewOrg",
    status_code=status.HTTP_201_CREATED,
    description="Create a new organization",
)
async def create_org(data: OrgCreate, db=Depends(get_mongo_db)):
    doc = {**data.dict(), "members": []}
    res = await db["organizations"].insert_one(doc)
    org = await db["organizations"].find_one({"_id": res.inserted_id})
    org["_id"] = str(org["_id"])
    return org


@router.post(
    "/orgs/{org_id}/addMember",
    description="Add a user to an organization",
)
async def add_member(org_id: str, data: AddMember, db=Depends(get_mongo_db)):
    oid = ObjectId(org_id)
    # 6860a1fbdbb773d18164f2b2
    check_user = await db["users"].find_one({"username": data.username}, {"_id": 0})
    if not check_user:
        return {"message": "User not found"}
    result = await db["organizations"].update_one(
        {"_id": oid},
        {"$addToSet": {"members": data.username}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Organization not found")
    org = await db["organizations"].find_one({"_id": oid})
    org["_id"] = org_id
    return org


@router.get("/orgs/{org_id}/getAllMemebers", description="Get all mementers of an organization")
async  def get_all_members(org_id: str, db=Depends(get_mongo_db)):
    oid = ObjectId(org_id)
    org = await db["organizations"].find_one({"_id": oid}, {"_id": 0, "members": 1})
    if not org:
        return {"message": "Organization not found"}
    return org


@router.get(
    "/orgs/{org_id}/avgExp",
    description="Average years of experience among this org’s members",
)
async def org_avg_experience(org_id: str, db=Depends(get_mongo_db)):
    oid = ObjectId(org_id)
    pipeline = [
        {"$match": {"_id": oid}},
        {"$lookup": {
            "from": "users",
            "localField": "members",
            "foreignField": "username",
            "as": "team"
        }},
        {"$unwind": "$team"},
        {"$group": {
            "_id": None,
            "average_experience": {"$avg": "$team.experience"}
        }},
        {"$project": {"_id": 0, "average_experience": 1}}
    ]
    res = await db["organizations"].aggregate(pipeline).to_list(length=1)
    return res[0] if res else {"average_experience": 0.0}


@router.get(
    "/orgs/{org_id}/orgSkillstats",
    description="Count of each skill among this org’s members",
)
async def org_skill_stats(org_id: str, db=Depends(get_mongo_db)):
    oid = ObjectId(org_id)
    pipeline = [
        {"$match": {"_id": oid}},
        {"$lookup": {
            "from": "users",
            "localField": "members",
            "foreignField": "username",
            "as": "team"
        }},
        {"$unwind": "$team"},
        {"$unwind": "$team.skills"},
        {"$group": {
            "_id": "$team.skills",
            "count": {"$sum": 1}
        }},
        {"$project": {"skill": "$_id", "count": 1, "_id": 0}},
        {"$sort": {"count": -1}}
    ]
    stats = await db["organizations"].aggregate(pipeline).to_list(length=None)
    return stats