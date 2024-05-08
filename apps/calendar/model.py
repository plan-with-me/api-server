from tortoise import fields

from core.base_orm import BaseEntity


class Calendar(BaseEntity):
    name = fields.CharField(max_length=32)
