from tortoise import fields

from core.base_orm import BaseEntity


class User(BaseEntity):
    uid = fields.CharField(max_length=64, unique=True)
    name = fields.CharField(max_length=16)
    introduction = fields.TextField()
    image = fields.CharField(max_length=256)
