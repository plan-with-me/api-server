from pydantic import BaseModel

from core.base_dto import BaseResponse


class UserResponse(BaseResponse):
    name: str
    introduction: str | None
    image: str | None


class UserUpdateForm(BaseModel):
    name: str
    introduction: str | None
    image: str | None
