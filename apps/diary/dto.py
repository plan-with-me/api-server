from pydantic import BaseModel

from core.base_dto import BaseResponse
from apps.goal.enum import ShowScope
from apps.user.dto import UserResponse


class DiaryForm(BaseModel):
    title: str
    icon: str
    content: dict
    show_scope: ShowScope


class DiaryResponse(BaseResponse):
    title: str
    icon: str
    content: dict
    show_scope: ShowScope
    user: UserResponse | None = None
