from fastapi import FastAPI
from routers.redis_router import router as redis_router

app = FastAPI()

# Include Redis router
app.include_router(redis_router)

@app.get("/")
def read_root():
    return {"message": "Ready!"}