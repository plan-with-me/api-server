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
    response_model=dto.CalendarSimpleResponse,
)
@atomic()
async def create_calendar(request: Request, form: dto.CalendarForm):
    form.user_ids.append(request.state.token_payload["id"])
    calendar = await model.Calendar.create(**form.__dict__)
    await util.set_users_on_calendar(
        calendar_id=calendar.id,
        new_user_ids=form.user_ids,
        validate_strictly=False,
    )
    return calendar


@router.get(
    path="",
    response_model=list[dto.CalendarSimpleResponse],
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
    dependencies=[Depends(CalendarPermission(get_calendar=True))],
    response_model=dto.CalendarResponse,
    description="""
    특정 공유 달력의 정보를 조회합니다.
    추가로 공유 달력 내 구성원 목록을 포함합니다.
    """
)
async def get_calendar_detail(request: Request, calendar_id: int):
    calendar = request.state.calendar_user.calendar
    users = await util.get_calendar_members(calendar_id)
    return dto.CalendarResponse(
        **calendar.__dict__,
        users=[user_dto.UserResponse.from_orm(user) for user in users]
    )


@router.put(
    path="/{calendar_id}",
    dependencies=[Depends(CalendarPermission(get_calendar=True))],
    response_model=dto.CalendarSimpleResponse,
)
@atomic()
async def update_calendar(
    request: Request, 
    calendar_id: int, 
    form: dto.CalendarForm,
):
    calendar: model.Calendar = request.state.calendar_user.calendar
    await util.set_users_on_calendar(
        calendar_id=calendar_id,
        new_user_ids=form.user_ids,
        validate_strictly=True,
    )
    await calendar.update_from_dict(form.__dict__)
    await calendar.save()
    return calendar


@router.delete(
    path="/{calendar_id}",
    dependencies=[Depends(CalendarPermission())],
)
@atomic()
async def delete_calendar(request: Request, calendar_id: int):
    result = await model.Calendar.filter(id=calendar_id).delete()
    return result
