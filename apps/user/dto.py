from pydantic import BaseModel

from core.base_dto import BaseResponse


class UserResponse(BaseResponse):
    name: str
    introduction: str | None
    image: str | None
    uid: str


class UserUpdateForm(BaseModel):
    name: str
    introduction: str | None
    image: str | None
