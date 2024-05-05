from pydantic import BaseModel
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    name: str
    introduction: str | None
    image: str | None
    created_at: datetime
    updated_at: datetime


class UserUpdateForm(BaseModel):
    name: str
    introduction: str | None
    image: str | None
