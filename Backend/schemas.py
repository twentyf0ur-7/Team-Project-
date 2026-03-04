from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
