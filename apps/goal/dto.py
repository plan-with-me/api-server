from pydantic import BaseModel
from datetime import datetime

from core.base_dto import BaseResponse
from apps.goal import enum


class TopGoalResponse(BaseResponse):
    name: str
    color: str
    status: enum.GoalStatus
    show_scope: str
    user_id: int
    tags: list[str] = []


class TopGoalAchievementRateResponse(BaseResponse):
    name: str
    color: str
    sub_goal_count: int = 0
    complete_count: int = 0


class TopGoalForm(BaseModel):
    name: str
    color: str = "skyblue"
    status: enum.GoalStatus
    show_scope: enum.ShowScope = enum.ShowScope.ME
    tags: list[str] = []


class SubGoalRepsonse(BaseResponse):
    top_goal_id: int
    name: str
    plan_datetime: datetime
    status: enum.GoalStatus
    user_id: int


class SubGoalForm(BaseModel):
    name: str
    plan_datetime: datetime
    status: enum.GoalStatus
