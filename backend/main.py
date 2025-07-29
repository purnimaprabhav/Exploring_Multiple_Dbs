from fastapi import FastAPI
from backend.app.routes.neo4j import user as neo4j_user
from backend.app.routes.mongo import user as mongo_user
from backend.app.routes.mongo import org as mongo_org
from backend.app.config.db.mongo_conn import lifespan as mongo_lifespan

app = FastAPI(lifespan=mongo_lifespan)

app.include_router(neo4j_user.router)

app.include_router(mongo_user.router)

app.include_router(mongo_org.router)
