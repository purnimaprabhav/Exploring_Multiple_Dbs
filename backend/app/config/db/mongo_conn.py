from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from pymongo.server_api import ServerApi
import os
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(
        MONGO_URI
    #     tls=True,
    #     tlsCAFile=certifi.where(),
    #     server_api=ServerApi("1")
        )
    db = client.get_database("nosql_project")
    app.state.mongodb = db
    yield
    client.close()

def get_mongo_db(request: Request):
    return request.app.state.mongodb