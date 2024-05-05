from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.user import model, dto


router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.get(
    path="/{user_id}",
    dependencies=[Depends(Auth())],
)
async def get_user(user_id: int):
    user = await model.User.get(id=user_id)
    return dto.UserResponse(**user.__dict__)


@router.put(
    path="/{user_id}",
    dependencies=[Depends(Auth())],
    description="본인의 프로필만 수정할 수 있습니다.",
)
@atomic()
async def update_user_profile(
    request: Request,
    user_id: int,
    form: dto.UserUpdateForm,
):
    if request.state.token_payload["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user = await model.User.get(id=user_id)
    await user.update_from_dict(form.__dict__)
    return dto.UserResponse(**user.__dict__)
