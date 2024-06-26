from tortoise import fields

from core.base_orm import BaseEntity
from apps.auth.enum import SocialType
from apps.user.enum import FollowStatus


class User(BaseEntity):
    uid = fields.CharField(max_length=64, unique=True)
    social_type = fields.CharEnumField(SocialType, max_length=12)
    name = fields.CharField(max_length=16)
    introduction = fields.TextField(null=True)
    image = fields.CharField(max_length=256, null=True)


class Follow(BaseEntity):
    user = fields.ForeignKeyField(model_name="models.User", related_name="followings")
    target_user = fields.ForeignKeyField(model_name="models.User", related_name="followers")
    status = fields.CharEnumField(enum_type=FollowStatus, max_length=16, default=FollowStatus.PENDING)
