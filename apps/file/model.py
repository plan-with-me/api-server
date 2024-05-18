from tortoise import fields

from core.base_orm import BaseEntity


class File(BaseEntity):
    original_filename = fields.CharField(max_length=256)
    user = fields.ForeignKeyField(model_name="models.User", related_name="files")
