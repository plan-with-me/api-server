from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.user import model, dto, enum


router = APIRouter(
    prefix="/users",
    tags=["User"],
    # dependencies=[Depends(Auth())],
)


@router.get(
    path="/me",
    response_model=dto.UserResponse,
)
async def get_my_user_info(request: Request):
    user = await model.User.get(id=request.state.token_payload["id"])
    return user


@router.get(
    path="/{user_id}",
    response_model=dto.UserResponse,
)
async def get_user(user_id: int):
    user = await model.User.get(id=user_id)
    return user


@router.put(
    path="/{user_id}",
    response_model=dto.UserResponse,
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
    await user.save()
    return user


@router.delete(
    path="/me",
    description="유저 본인을 삭제합니다. (Hard Deletion)",
    status_code=status.HTTP_200_OK,
)
@atomic()
async def delete_user_me(request: Request):
    result = await model.User.filter(id=request.state.token_payload["id"]).delete()
    return result


@router.post(
    path="/{user_id}/follow",
)
async def follow_user(request: Request, user_id: int):
    request_user_id = request.token_payload["id"]
    follow = await model.Follow.create(
        user_id=request_user_id,
        target_user_id=user_id,
    )


@router.get(
    path="/{user_id}/{kind}",
    response_model=list[dto.UserResponse],
)
async def get_follows(
    request: Request,
    user_id: int,
    kind: enum.FollowKind = enum.FollowKind.FOLLOWERS,
):
    if kind == enum.FollowKind.FOLLOWERS:
        attr = "user"
        follows = await model.Follow.filter(target_user_id=user_id).select_related("user")
    elif kind == enum.FollowKind.FOLLOWINGS:
        attr = "target_user"
        follows = await model.Follow.filter(user_id=user_id).select_related("target_user")
    return [follow.__getattribute__(attr) for follow in follows]
