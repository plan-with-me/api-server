from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.user import model, dto, enum, util


router = APIRouter(
    prefix="/users",
    tags=["User"],
    dependencies=[Depends(Auth())],
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
    user.update_from_dict(form.__dict__)
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
    responses={
        status.HTTP_200_OK: {"model": None},
        status.HTTP_400_BAD_REQUEST: {"model": None},
        status.HTTP_409_CONFLICT: {"model": None},
    },
    description="""
    요청한 유저가 `user_id`에 해당하는 유저를 팔로우합니다.  
    - 자기 자신에게 팔로우하면 **400 오류**를 응답합니다.  
    - 이미 팔로우중인 유저에게 팔로우하면 **409 오류**를 응답합니다.
    """
)
@atomic()
async def follow_user(request: Request, user_id: int):
    request_user_id = request.state.token_payload["id"]
    if user_id == request_user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if await util.check_is_following(request_user_id, user_id):
        raise HTTPException(status.HTTP_409_CONFLICT)
    await model.Follow.create(
        user_id=request_user_id,
        target_user_id=user_id,
    )
    return None


@router.get(
    path="/{user_id}/{follow_kind}",
    response_model=list[dto.UserResponse],
)
async def get_follows(
    user_id: int,
    follow_kind: enum.FollowKind = enum.FollowKind.FOLLOWERS,
):
    if follow_kind == enum.FollowKind.FOLLOWERS:
        attr = "user"
        follows = await model.Follow.filter(target_user_id=user_id).select_related("user")
    elif follow_kind == enum.FollowKind.FOLLOWINGS:
        attr = "target_user"
        follows = await model.Follow.filter(user_id=user_id).select_related("target_user")
    return [follow.__getattribute__(attr) for follow in follows]


@router.delete(
    path="/{user_id}/follow",
)
@atomic()
async def delete_follow(request: Request, user_id: int):
    result = await model.Follow.filter(
        user_id=request.state.token_payload["id"],
        target_user_id=user_id,
    ).delete()
    return result
