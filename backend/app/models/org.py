from pydantic import BaseModel, Field
from typing import List, Optional


class OrgCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AddMember(BaseModel):
    username: str