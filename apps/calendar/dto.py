from pydantic import BaseModel

from core.base_dto import BaseResponse
from apps.user import dto as user_dto


class CalendarResponse(BaseResponse):
    name: str
    introduction: str | None = None
    image: str | None


class CalendarPermissionResponse(BaseResponse):
    calendar_id: int
    user_id: int
    is_admin: bool


class CalendarUserResponse(user_dto.UserResponse):
    is_admin: bool


class CalendarForm(BaseModel):
    name: str
    introduction: str | None = None
    image: str | None = None
