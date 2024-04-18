from tortoise import fields

from core.base_orm import BaseEntity
from apps.auth.enum import SocialType


class User(BaseEntity):
    uid = fields.CharField(max_length=64, unique=True)
    social_type = fields.CharEnumField(SocialType, max_length=12)
    name = fields.CharField(max_length=16)
    introduction = fields.TextField()
    image = fields.CharField(max_length=256)
