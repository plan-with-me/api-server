from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.calendar import model, dto, util
from apps.user import dto as user_dto
from apps.goal import model as goal_model
from apps.goal import enum as goal_enum


router = APIRouter(
    prefix="/calendars",
    tags=["Calendar"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="",
    response_model=dto.CalendarResponse,
)
@atomic()
async def create_calendar(request: Request, form: dto.CalendarForm):
    form.user_ids.append(request.state.token_payload["id"])
    calendar = await model.Calendar.create(**form.__dict__)
    await util.add_users_on_calendar(
        calendar_id=calendar.id,
        user_ids=form.user_ids,
        validate_strictly=False,
    )
    users = await util.get_calendar_members(calendar.id)
    return dto.CalendarResponse(
        **calendar.__dict__, 
        users=[user_dto.UserResponse.from_orm(user) for user in users],
    )


@router.get(
    path="",
    response_model=list[dto.CalendarResponse],
)
async def get_calendars(
    request: Request, 
    form: dto.CalendarForm, 
    user_id: int=None,
):
    pass


@router.put(
    path="/{calendar_id}",
)
@atomic()
async def update_calendar(
    request: Request, 
    calendar_id: int, 
    form: dto.CalendarForm,
):
    pass


@router.delete(
    path="/{calendar_id}",
)
@atomic()
async def delete_calendar(request: Request, calendar_id: int):
    pass
