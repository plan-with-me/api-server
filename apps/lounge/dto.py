from pydantic import BaseModel
from apps.goal.dto import *


class TagsResponse(BaseModel):
    tags: list[str] = []


class TopGoalWithSubGoals(TopGoalResponse):
    sub_goals: list[SubGoalRepsonse] = []


class UserGoalsResponse(BaseModel):
    id: int
    name: str
    introduction: str | None
    image: str | None
    top_goals: list[TopGoalWithSubGoals] = []
