from typing import Any
from pydantic import BaseModel

from core.base_dto import BaseResponse
# from apps.user import dto as user_dto


class CalendarResponse(BaseResponse):
    name: str
    introduction: str | None = None
    image: str | None


class CalendarForm(BaseModel):
    name: str
    introduction: str | None = None
    image: str | None = None
    # user_ids: list[int] = []
