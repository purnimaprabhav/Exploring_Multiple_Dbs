from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    name: str
    number: str
    email: str
    role: str
    skills: List[str]
    experience: int
    interests: List[str]
    organization: str
    availability: bool


class UserLogin(BaseModel):
    username: str

class AvailabilityUpdate(BaseModel):
    username: str
    availability: bool