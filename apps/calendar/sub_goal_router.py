from fastapi import APIRouter, Depends, Request, status, HTTPException

from datetime import date
from tortoise.transactions import atomic
from tortoise.expressions import Q

from core.dependencies import Auth, CalendarPermission
from apps.goal import model, dto, enum


router = APIRouter(
    prefix="/calendars/{calendar_id}/sub-goals",
    tags=["Calendar Goals"],
    dependencies=[
        Depends(Auth()), 
        Depends(CalendarPermission()),
    ],
)


@router.post(
    path="",
    response_model=dto.SubGoalRepsonse,
)
@atomic()
async def create_sub_goal(
    request: Request, 
    calendar_id: int, 
    top_goal_id: int,
    form: dto.SubGoalForm,
):
    sub_goal = await model.SubGoal.create(
        **form.__dict__,
        top_goal_id=top_goal_id,
        user_id=request.state.token_payload["id"],
        calendar_id=calendar_id,
    )
    return sub_goal


@router.get(
    path="",
    response_model=list[dto.SubGoalRepsonse],
    description="""
    공유 달력의 하위 목표를 월별로 조회합니다.  
    `plan_date` 파라미터는 yyyy-mm 형태로 입력하며 입력하지 않을 경우 기본값으로 현재 년-월이 입력됩니다. 
    """,
)
async def get_sub_goals(
    request: Request,
    calendar_id: int,
    plan_date: str = date.today().strftime("%Y-%m"),
):
    query_set = model.SubGoal.filter(
        calendar_id=calendar_id,
        plan_datetime__startswith=plan_date,
    )
    query_set = query_set.filter(
        Q(calendar_id=calendar_id) &
        Q(plan_datetime__startswith=plan_date) &
        (
            Q(top_goal__show_scope=enum.ShowScope.GROUP) |
            (
                Q(top_goal__show_scope=enum.ShowScope.ME) &
                Q(top_goal__user_id=request.state.token_payload["id"])
            )
        )
    )
    sub_goals = await query_set.all()
    return sub_goals


@router.put(
    path="/{sub_goal_id}",
    response_model=dto.SubGoalRepsonse,
)
@atomic()
async def update_sub_goal(
    calendar_id: int, 
    sub_goal_id: int,
    form: dto.TopGoalForm,
):
    sub_goal = await model.SubGoal.get(
        id=sub_goal_id,
        calendar_id=calendar_id,
    )
    sub_goal.update_from_dict(form.__dict__)
    await sub_goal.save()
    return sub_goal


@router.delete(
    path="/{sub_goal_id}",
)
@atomic()
async def delete_sub_goal(calendar_id: int, sub_goal_id: int):
    result = await model.SubGoal.filter(
        id=sub_goal_id,
        calendar_id=calendar_id,
    ).delete()
    return result
