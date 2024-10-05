from tortoise import fields

from core.base_orm import BaseEntity
from apps.goal.enum import GoalStatus, ShowScope, ReactionType


class TopGoal(BaseEntity):
    name = fields.CharField(max_length=32)
    color = fields.CharField(max_length=16, default="skyblue")
    status = fields.CharEnumField(GoalStatus, max_length=16, default=GoalStatus.INCOMPLETE)
    show_scope = fields.CharEnumField(ShowScope, max_length=16, default=ShowScope.ME)
    user = fields.ForeignKeyField(model_name="models.User", related_name="top_goals")
    calendar = fields.ForeignKeyField(model_name="models.Calendar", related_name="top_goals", null=True)
    tags = fields.JSONField(default=[])
    related_tags = fields.JSONField(default=[])


class SubGoal(BaseEntity):
    name = fields.CharField(max_length=128)
    plan_datetime = fields.DatetimeField()
    status = fields.CharEnumField(GoalStatus, max_length=16, default=GoalStatus.INCOMPLETE)
    user = fields.ForeignKeyField(model_name="models.User", related_name="sub_goals")
    top_goal = fields.ForeignKeyField(model_name="models.TopGoal", related_name="sub_goals")
    calendar = fields.ForeignKeyField(model_name="models.Calendar", related_name="sub_goals", null=True)


class Reaction(BaseEntity):
    type = fields.CharEnumField(ReactionType, max_length=16)
    content = fields.TextField()
    user = fields.ForeignKeyField(model_name="models.User", related_name="reacts")
    sub_goal = fields.ForeignKeyField(model_name="models.SubGoal", related_name="reacts")
