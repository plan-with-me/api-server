from pydantic import BaseModel
from datetime import datetime


class TodoGroupResponse(BaseModel):
    id: int
    name: str
    description: str | None
    show_scope: str
    created_at: datetime
    updated_at: datetime


class TodoGroupForm(BaseModel):
    name: str
    description: str | None


class TodoRepsonse(BaseModel):
    id: int
    todo_group_id: int
    name: str
    description: str | None
    plan_datetime: datetime
    created_at: datetime
    updated_at: datetime


class TodoForm(BaseModel):
    name: str
    description: str | None
    plan_datetime: datetime
