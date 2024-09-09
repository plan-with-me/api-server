from tortoise import fields

from core.base_orm import BaseEntity
from apps.goal.enum import ShowScope


class Diary(BaseEntity):
    title = fields.CharField(max_length=256)
    icon = fields.CharField(max_length=256)
    content = fields.JSONField()
    show_scope = fields.CharEnumField(ShowScope, default=ShowScope.ME)
    user = fields.ForeignKeyField(model_name="models.User", related_name="diaries")
    date = fields.DateField()
