import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from backend.app.api import neo4j_api

app = FastAPI()
app.include_router(neo4j_api.router)
