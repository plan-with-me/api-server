from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependencies import Auth, CalendarPermission
from apps.calendar import model, dto, util
from apps.user import dto as user_dto


router = APIRouter(
    prefix="/calendars",
    tags=["Calendar"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="",
    response_model=dto.CalendarResponse,
    description="""공유 달력을 생성합니다."""
)
@atomic()
async def create_calendar(request: Request, form: dto.CalendarForm):
    calendar = await model.Calendar.create(**form.__dict__)
    await model.CalendarUser.create(
        user_id=request.state.token_payload["id"],
        calendar_id=calendar.id,
    )
    # form.user_ids.append(request.state.token_payload["id"])
    # await util.set_users_on_calendar(
    #     calendar_id=calendar.id,
    #     new_user_ids=form.user_ids,
    #     validate_strictly=False,
    # )
    return calendar


@router.get(
    path="",
    response_model=list[dto.CalendarResponse],
    description="""
    특정 유저의 공유 달력을 모두 조회합니다.   
    본인의 공유 달력을 조회할 경우 `user_id` 파라미터를 포함하지 않고 요청합니다.
    """
)
async def get_calendar_list(request: Request, user_id: int = None):
    user_id = user_id if user_id else request.state.token_payload["id"]
    calendar_users = await model.CalendarUser.filter(user_id=user_id).select_related("calendar").all()
    return [calendar_user.calendar for calendar_user in calendar_users]


@router.get(
    path="/{calendar_id}",
    response_model=dto.CalendarResponse,
    description="""특정 공유 달력 정보를 조회합니다.""",
)
async def get_calendar(request: Request, calendar_id: int):
    calendar = await model.Calendar.get(id=calendar_id)
    return calendar


@router.put(
    path="/{calendar_id}",
    dependencies=[Depends(CalendarPermission(get_calendar=True))],
    response_model=dto.CalendarResponse,
    description="""
    공유 달력 정보를 수정합니다.
    """
)
@atomic()
async def update_calendar(
    request: Request, 
    calendar_id: int, 
    form: dto.CalendarForm,
):
    calendar: model.Calendar = request.state.calendar_user.calendar
    # await util.set_users_on_calendar(
    #     calendar_id=calendar_id,
    #     new_user_ids=form.user_ids,
    #     validate_strictly=True,
    # )
    await calendar.update_from_dict(form.__dict__).save()
    return calendar


@router.delete(
    path="/{calendar_id}",
    dependencies=[Depends(CalendarPermission())],
)
@atomic()
async def delete_calendar(request: Request, calendar_id: int):
    result = await model.Calendar.filter(id=calendar_id).delete()
    return result


@router.get(
    path="/{calendar_id}/users",
    dependencies=[Depends(CalendarPermission())],
    response_model=list[user_dto.UserResponse],
    description="공유 달력 내 구성원 목록을 조회합니다.",
)
async def get_calendar_users(request: Request, calendar_id: int):
    users = await util.get_calendar_members(calendar_id)
    return users


@router.post(
    path="/{calendar_id}/users/{user_id}",
    dependencies=[Depends(CalendarPermission())],
    description="""
    공유 달력에 구성원을 추가합니다.   
    해당 유저가 존재하지 않을 경우 **400 오류**를 응답합니다.   
    해당 유저가 이미 구성원일 경우 **409 오류**를 응답합니다.
    """,
)
async def add_calendar_user(
    calendar_id: int,
    user_id: int,
):
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


@router.delete(
    path="/{calendar_id}/users/{user_id}",
    dependencies=[Depends(CalendarPermission(get_calendar=True))],
    description="""
    공유 달력에 구성원을 삭제합니다.   
    해당 유저가 존재하지 않을 경우 **400 오류**를 응답합니다.   
    해당 유저가 이미 구성원일 경우 **409 오류**를 응답합니다.
    """
)
async def delete_calender_user(
    request: Request,
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
