from pydantic import BaseModel
from datetime import datetime

from apps.goal import model


class TopGoalResponse(BaseModel):
    id: int
    name: str
    color: str
    status: str
    show_scope: str
    created_at: datetime
    updated_at: datetime


class TopGoalForm(BaseModel):
    name: str
    color: str = "skyblue"
    show_scope: str = model.ShowScope.ME


class SubGoalRepsonse(BaseModel):
    id: int
    top_goal_id: int
    name: str
    plan_datetime: datetime
    created_at: datetime
    updated_at: datetime


class SubGoalForm(BaseModel):
    name: str
    plan_datetime: datetime
    status: str
