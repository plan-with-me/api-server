from pydantic import BaseModel
from tortoise import models
from datetime import datetime


class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, orm: models.Model, **kwargs):
        return cls(
            **orm.__dict__,
            **kwargs,
        )
