from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.user import model, dto


router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.get(
    path="/me",
    dependencies=[Depends(Auth())],
    response_model=dto.UserResponse,
)
async def get_my_user_info(request: Request):
    user = await model.User.get(id=request.state.token_payload["id"])
    return dto.UserResponse.from_orm(user)


@router.get(
    path="/{user_id}",
    dependencies=[Depends(Auth())],
    response_model=dto.UserResponse,
)
async def get_user(user_id: int):
    user = await model.User.get(id=user_id)
    return dto.UserResponse.from_orm(user)


@router.put(
    path="/{user_id}",
    dependencies=[Depends(Auth())],
    description="본인의 프로필을 수정합니다.",
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
    return dto.UserResponse.from_orm(user)


@router.delete(
    path="/me",
    dependencies=[Depends(Auth())],
    description="유저 본인을 삭제합니다. (Hard Deletion)",
    status_code=status.HTTP_200_OK,
)
@atomic()
async def delete_user_me(request: Request):
    result = await model.User.filter(id=request.state.token_payload["id"]).delete()
    return 
