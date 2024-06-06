from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependencies import Auth, CalendarPermission
from apps.calendar import model, dto


router = APIRouter(
    prefix="/calendars",
    tags=["Calendar"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="",
    response_model=dto.CalendarResponse,
    description="""공유 달력을 생성합니다. 생성한 유저는 관리자 권한을 가집니다."""
)
@atomic()
async def create_calendar(request: Request, form: dto.CalendarForm):
    calendar = await model.Calendar.create(**form.__dict__)
    await model.CalendarUser.create(
        user_id=request.state.token_payload["id"],
        calendar_id=calendar.id,
        is_admin=True,
    )
    return calendar


@router.get(
    path="",
    response_model=list[dto.CalendarResponse],
    description="""
    특정 유저의 공유 달력을 모두 조회합니다.   
    본인의 공유 달력을 조회할 경우 `user_id` 파라미터를 포함하지 않고 요청합니다.   
    `admin` 파라미터를 포함할 경우 해당 유저가 관리자 권한을 가지고 있는 달력만 조회합니다.   
    """
)
async def get_calendar_list(
    request: Request, 
    user_id: int = None,
    admin: bool = False,
):
    user_id = user_id if user_id else request.state.token_payload["id"]
    query_set = model.CalendarUser.filter(user_id=user_id).select_related("calendar")
    if admin:
        query_set = query_set.filter(is_admin=True)
    calendar_users = await query_set.all()
    return [calendar_user.calendar for calendar_user in calendar_users]


@router.get(
    path="/{calendar_id}",
    response_model=dto.CalendarResponse,
    description="""특정 공유 달력 정보를 조회합니다.""",
)
async def get_calendar(calendar_id: int):
    calendar = await model.Calendar.get(id=calendar_id)
    return calendar


@router.get(
    path="/{calendar_id}/permission",
    response_model=dto.CalendarPermissionResponse,
    description="""특정 공유 달력에서 본인이 관리자 권한을 가지고 있는지 확인합니다.""",
)
async def get_calendar_permission(request: Request, calendar_id: int):
    calendar_user = await model.CalendarUser.get(
        calendar_id=calendar_id,
        user_id=request.state.token_payload["id"],
    )
    return calendar_user


@router.put(
    path="/{calendar_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True, get_calendar=True))],
    response_model=dto.CalendarResponse,
    description="""
    공유 달력 정보를 수정합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.
    """
)
@atomic()
async def update_calendar(
    request: Request, 
    calendar_id: int, 
    form: dto.CalendarForm,
):
    calendar: model.Calendar = request.state.calendar_user.calendar
    await calendar.update_from_dict(form.__dict__).save()
    return calendar


@router.delete(
    path="/{calendar_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True))],
    description="""
    공유 달력을 삭제합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.
    """
)
@atomic()
async def delete_calendar(calendar_id: int):
    result = await model.Calendar.filter(id=calendar_id).delete()
    return result


@router.get(
    path="/{calendar_id}/users",
    dependencies=[Depends(CalendarPermission())],
    response_model=list[dto.CalendarUserResponse],
    description="공유 달력 내 구성원 목록을 조회합니다.",
)
async def get_calendar_users(calendar_id: int):
    calendar_users = await (
        model.CalendarUser
        .filter(calendar_id=calendar_id)
        .select_related("user")
        .all()
    )
    users = [
        dto.CalendarUserResponse(**cu.user.__dict__, is_admin=cu.is_admin)
        for cu in calendar_users
    ]
    return users


@router.post(
    path="/{calendar_id}/users/{user_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True))],
    description="""
    공유 달력에 구성원을 추가합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.   
    - 해당 유저가 존재하지 않을 경우 **400 오류**를 응답합니다.   
    - 해당 유저가 이미 구성원일 경우 **409 오류**를 응답합니다.
    """,
)
async def add_calendar_user(calendar_id: int, user_id: int):
    if await model.CalendarUser.exists(
        calendar_id=calendar_id,
        user_id=user_id,
    ):
        raise HTTPException(status.HTTP_409_CONFLICT)
    await model.CalendarUser.create(
        calendar_id=calendar_id,
        user_id=user_id,
    )
    return True


@router.put(
    path="/{calendar_id}/users/{user_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True))],
    description="""
    공유 달력 구성원의 권한을 수정합니다.(관리자/사용자)   
    `admin`이 true일 경우 관리자, false일 경우 일반 유저 권한으로 수정합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.
    - 해당 유저가 존재하지 않을 경우 **400 오류**를 응답합니다.   
    """,
)
async def update_calender_user_permission(
    calendar_id: int,
    user_id: int,
    admin: bool = True,
):
    calendar_user = await model.CalendarUser.get(calendar_id=calendar_id, user_id=user_id)
    calendar_user.is_admin = admin
    await calendar_user.save()
    return True


@router.delete(
    path="/{calendar_id}/users/{user_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True, get_calendar=True))],
    description="""
    공유 달력에 구성원을 삭제합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.   
    - 해당 유저가 존재하지 않을 경우 **400 오류**를 응답합니다.   
    - 해당 유저가 이미 구성원일 경우 **409 오류**를 응답합니다.
    """
)
async def delete_calender_user(
    calendar_id: int,
    user_id: int,
):
    result = await model.CalendarUser.filter(
        calendar_id=calendar_id,
        user_id=user_id,
    ).delete()
    if not result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return result
