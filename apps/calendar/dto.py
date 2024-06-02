from typing import Any
from pydantic import BaseModel

from core.base_dto import BaseResponse
from apps.user import dto as user_dto


class CalendarSimpleResponse(BaseResponse):
    name: str
    image: str | None


class CalendarForm(BaseModel):
    name: str
    image: str | None = None
    # user_ids: list[int] = []
