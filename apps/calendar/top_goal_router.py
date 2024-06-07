from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependencies import Auth, CalendarPermission
from apps.goal import model as goal_model
from apps.goal import dto as goal_dto


router = APIRouter(
    prefix="/calendars/{calendar_id}/top-goals",
    tags=["Calendar Goals"],
    dependencies=[
        Depends(Auth()), 
    ],
)


@router.post(
    path="",
    dependencies=[Depends(CalendarPermission(check_admin=True))],
    response_model=goal_dto.TopGoalResponse,
    description="""
    상위 목표를 생성합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.
    """
)
@atomic()
async def create_top_goal(
    request: Request, 
    calendar_id: int, 
    form: goal_dto.TopGoalForm,
):
    top_goal = await goal_model.TopGoal.create(
        **form.__dict__,
        user_id=request.state.token_payload["id"],
        calendar_id=calendar_id,
    )
    return top_goal


@router.get(
    path="",
    dependencies=[Depends(CalendarPermission())],
    response_model=list[goal_dto.TopGoalResponse],
)
async def get_top_goals(calendar_id: int):
    top_goals = await goal_model.TopGoal.filter(calendar_id=calendar_id).all()
    return top_goals


@router.put(
    path="/{top_goal_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True))],
    response_model=goal_dto.TopGoalResponse,
    description="""
    상위 목표를 수정합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.
    """
)
@atomic()
async def update_top_goal(
    calendar_id: int, 
    top_goal_id: int,
    form: goal_dto.TopGoalForm,
):
    top_goal = await goal_model.TopGoal.get(
        id=top_goal_id,
        calendar_id=calendar_id,
    )
    top_goal.update_from_dict(form.__dict__)
    await top_goal.save()
    return top_goal


@router.delete(
    path="/{top_goal_id}",
    dependencies=[Depends(CalendarPermission(check_admin=True))],
    description="""
    상위 목표를 삭제합니다.   
    - 관리자가 아닌 유저가 시도할 경우 **403 오류**를 응답합니다.
    """
)
@atomic()
async def delete_top_goal(calendar_id: int, top_goal_id: int):
    result = await goal_model.TopGoal.filter(
        id=top_goal_id,
        calendar_id=calendar_id,
    ).delete()
    return result
