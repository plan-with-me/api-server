from enum import Enum
from tortoise import fields

from core.base_orm import BaseEntity


class ShowScope(Enum):
    ME = "me"
    FOLLWERS = "followers"
    ALL = "all"


class GoalStatus(Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class TopGoal(BaseEntity):
    name = fields.CharField(max_length=16)
    color = fields.CharField(max_length=16, default="skyblue")
    status = fields.CharEnumField(GoalStatus, max_length=16, default=GoalStatus.INCOMPLETE)
    show_scope = fields.CharEnumField(ShowScope, max_length=16, default=ShowScope.ME)
    user = fields.ForeignKeyField(model_name="models.User", related_name="top_goals")


class SubGoal(BaseEntity):
    name = fields.CharField(max_length=128)
    plan_datetime = fields.DatetimeField()
    status = fields.CharEnumField(GoalStatus, max_length=16, default=GoalStatus.INCOMPLETE)
    user = fields.ForeignKeyField(model_name="models.User", related_name="sub_goals")
    top_goal = fields.ForeignKeyField(model_name="models.TopGoal", related_name="sub_goals")
