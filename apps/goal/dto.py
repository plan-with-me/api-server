from pydantic import BaseModel
from datetime import datetime

from core.base_dto import BaseResponse
from apps.goal import model


class TopGoalResponse(BaseResponse):
    name: str
    color: str
    status: model.GoalStatus
    show_scope: str


class TopGoalForm(BaseModel):
    name: str
    color: str = "skyblue"
    status: model.GoalStatus
    show_scope: model.ShowScope = model.ShowScope.ME


class SubGoalRepsonse(BaseResponse):
    top_goal_id: int
    name: str
    plan_datetime: datetime
    status: model.GoalStatus


class SubGoalForm(BaseModel):
    name: str
    plan_datetime: datetime
    status: model.GoalStatus
