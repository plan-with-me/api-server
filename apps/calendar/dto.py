from typing import Any
from pydantic import BaseModel

from core.base_dto import BaseResponse
from apps.user import dto as user_dto


class CalendarResponse(BaseResponse):
    name: str
    image: str
    users: list[user_dto.UserResponse] = []


class CalendarForm(BaseModel):
    name: str
    image: str = None
    user_ids: list[int] = []
