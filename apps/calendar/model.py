from tortoise import fields

from core.base_orm import BaseEntity


class Calendar(BaseEntity):
    name = fields.CharField(max_length=32)
    introduction = fields.TextField(null=True)
    image = fields.CharField(max_length=256, null=True)


class CalendarUser(BaseEntity):
    user = fields.ForeignKeyField(model_name="models.User", related_name="calendars")
    calendar = fields.ForeignKeyField(model_name="models.Calendar", related_name="users")
