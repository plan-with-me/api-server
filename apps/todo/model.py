from enum import Enum
from tortoise import fields

from core.base_orm import BaseEntity


class ShowScope(Enum):
    ME = "me"
    FOLLWERS = "followers"
    ALL = "all"


class TodoGroup(BaseEntity):
    name = fields.CharField(max_length=16)
    description = fields.TextField(null=True)
    user = fields.ForeignKeyField(model_name="models.User", related_name="todo_groups")
    show_scope = fields.CharEnumField(ShowScope, max_length=16, default=ShowScope.ALL)


class Todo(BaseEntity):
    name = fields.CharField(max_length=64)
    description = fields.TextField(null=True)
    plan_datetime = fields.DatetimeField()
    user = fields.ForeignKeyField(model_name="models.User", related_name="todos")
    todo_group = fields.ForeignKeyField(model_name="models.TodoGroup", related_name="todos")
