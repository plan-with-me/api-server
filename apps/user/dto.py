from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    introduction: str | None
    image: str | None


class UserUpdateForm(BaseModel):
    name: str
    introduction: str | None
    image: str | None
