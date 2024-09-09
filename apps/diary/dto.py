from pydantic import BaseModel
import datetime as dt

from core.base_dto import BaseResponse
from apps.goal.enum import ShowScope
from apps.user.dto import UserResponse


class DiaryForm(BaseModel):
    title: str
    icon: str
    content: dict
    show_scope: ShowScope
    date: dt.date


class DiaryResponse(BaseResponse):
    title: str
    icon: str
    content: dict
    show_scope: ShowScope
    user: UserResponse | None = None
    date: dt.date
