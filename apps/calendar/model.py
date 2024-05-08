from tortoise import fields

from core.base_orm import BaseEntity


class Calendar(BaseEntity):
    name = fields.CharField(max_length=32)


class CalendarUser(BaseEntity):
    user = fields.ForeignKeyField(model_name="model.User", related_name="calendars")
    calendar = fields.ForeignKeyField(model_name="model.Calendar", related_name="users")
