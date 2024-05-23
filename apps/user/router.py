from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependencies import Auth
from apps.user import model, dto, enum, util


router = APIRouter(
    prefix="/users",
    tags=["User"],
    dependencies=[Depends(Auth())],
)


@router.get(
    path="",
    response_model=list[dto.UserResponse],
)
async def search_user(email: str):
    users = await model.User.filter(
        uid__contains=email,
    ).limit(5)
    return users


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
    path="/{user_id}/follows",
    responses={
        status.HTTP_200_OK: {"model": None},
        status.HTTP_400_BAD_REQUEST: {"model": None},
        status.HTTP_409_CONFLICT: {"model": None},
    },
    description="""
    요청한 유저가 `user_id`에 해당하는 유저를 팔로우합니다.  
    - 자기 자신 또는 존재하지 않는 유저를 팔로우할 경우 **400 오류**를 응답합니다.  
    - 이미 해당 유저에게 팔로우 요청을 보냈거나 팔로우중이라면 **409 오류**를 응답합니다.
    """
)
@atomic()
async def request_follow_user(request: Request, user_id: int):
    request_user_id = request.state.token_payload["id"]
    if user_id == request_user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    
    follow = await model.Follow.get_or_none(
        user_id=request_user_id,
        target_user_id=user_id,
    )
    if follow:
        raise HTTPException(status.HTTP_409_CONFLICT)
    else:
        await model.Follow.create(
            user_id=request_user_id,
            target_user_id=user_id,
        )
    return True


@router.get(
    path="/{user_id}/follows",
    response_model=list[dto.UserResponse],
    description="""
    특정 유저의 팔로우 정보를 조회합니다.  
    **pending** 상태인 팔로우 정보는 본인만 확인할 수 있습니다.   
    - 본인의 보류중인 팔로우 요청 목록 조회는 본인만 가능합니다.
    """
)
async def get_follows(
    request: Request,
    user_id: int,
    kind: enum.FollowKind = enum.FollowKind.FOLLOWERS,
    stat: enum.FollowStatus = enum.FollowStatus.ACCEPTED,
):
    if (
        request.state.token_payload["id"] != user_id and
        stat == enum.FollowStatus.PENDING
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    
    if kind == enum.FollowKind.FOLLOWERS:
        attr = "user"
        follows = await model.Follow.filter(
            target_user_id=user_id,
            status=stat,
        ).select_related(attr)
    elif kind == enum.FollowKind.FOLLOWINGS:
        attr = "target_user"
        follows = await model.Follow.filter(
            user_id=user_id,
            status=stat,
        ).select_related(attr)
    return [follow.__getattribute__(attr) for follow in follows]


@router.put(
    path="/{user_id}/follows",
    description="""
    요청한 유저가 `user_id`에 해당하는 유저의 팔로우 요청을 수락합니다.
    """,
)
@atomic()
async def accept_follows(
    request: Request,
    user_id: int,
):
    result = await model.Follow.filter(
        user_id=user_id,
        target_user_id=request.state.token_payload["id"],
    ).update(
        status=enum.FollowStatus.ACCEPTED,
    )
    if not result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return True


@router.delete(
    path="/{user_id}/follows",
    description="""
    요청한 유저가 `user_id`에 해당하는 유저의 팔로우를을 삭제합니다.   
    - kind가 **followers**인 경우 `user_id`에 해당하는 유저가 나에게 보낸 팔로우 요청을 삭제합니다.   
    - kind가 **followings**인 경우 내가 `user_id`에 해당하는 유저에게 보낸 팔로우 요청을 삭제합니다.
    """
)
@atomic()
async def delete_follow(
    request: Request, 
    user_id: int,
    kind: enum.FollowKind = enum.FollowKind.FOLLOWERS,
):
    request_user_id = request.state.token_payload["id"]
    if kind == enum.FollowKind.FOLLOWERS:
        result = await model.Follow.filter(
            user_id=user_id,
            target_user_id=request_user_id,
        ).delete()
    elif kind == enum.FollowKind.FOLLOWINGS:
        result = await model.Follow.filter(
            user_id=request_user_id,
            target_user_id=user_id,
        ).delete()
    if not result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return True
