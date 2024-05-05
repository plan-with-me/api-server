from enum import Enum
from tortoise import fields

from core.base_orm import BaseEntity


class ShowScope(Enum):
    ME = "me"
    FOLLWERS = "followers"
    ALL = "all"


class GoalStatus(Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


class TopGoal(BaseEntity):
    name = fields.CharField(max_length=16)
    description = fields.TextField(null=True)
    user = fields.ForeignKeyField(model_name="models.User", related_name="top_goals")
    show_scope = fields.CharEnumField(ShowScope, max_length=16, default=ShowScope.ME)
    status = fields.CharEnumField(GoalStatus, max_length=16, default=GoalStatus.INCOMPLETE)


class SubGoal(BaseEntity):
    name = fields.CharField(max_length=64)
    description = fields.TextField(null=True)
    plan_datetime = fields.DatetimeField()
    user = fields.ForeignKeyField(model_name="models.User", related_name="sub_goals")
    top_goal = fields.ForeignKeyField(model_name="models.TopGoal", related_name="sub_goals")
