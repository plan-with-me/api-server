from typing import (
    Any, 
    TypeVar,
    Coroutine, 
    Iterable,
)
from tortoise import fields
from tortoise.models import Model
from tortoise.backends.base.client import BaseDBAsyncClient
from datetime import datetime


MODEL = TypeVar("MODEL", bound="Model")

class BaseEntity(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    async def save(
        self, 
        using_db: BaseDBAsyncClient | None = None, 
        update_fields: Iterable[str] | None = None, 
        force_create: bool = False, 
        force_update: bool = False
    ) -> Coroutine[Any, Any, None]:
        self.updated_at = datetime.now()
        return await super().save(using_db, update_fields, force_create, force_update)
