from pydantic import BaseModel
from datetime import datetime


class TopGoalResponse(BaseModel):
    id: int
    name: str
    description: str | None
    show_scope: str
    created_at: datetime
    updated_at: datetime


class TopGoalForm(BaseModel):
    name: str
    description: str | None


class SubGoalRepsonse(BaseModel):
    id: int
    todo_group_id: int
    name: str
    description: str | None
    plan_datetime: datetime
    created_at: datetime
    updated_at: datetime


class SubGoalForm(BaseModel):
    name: str
    description: str | None
    plan_datetime: datetime
