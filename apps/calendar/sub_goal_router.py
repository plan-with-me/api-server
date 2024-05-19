from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependencies import Auth, CalendarPermission
from apps.goal import model as goal_model
from apps.goal import dto as goal_dto


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
    response_model=goal_dto.SubGoalRepsonse,
)
@atomic()
async def create_sub_goal(
    request: Request, 
    calendar_id: int, 
    top_goal_id: int,
    form: goal_dto.SubGoalForm,
):
    sub_goal = await goal_model.SubGoal.create(
        **form.__dict__,
        top_goal_id=top_goal_id,
        user_id=request.state.token_payload["id"],
        calendar_id=calendar_id,
    )
    return sub_goal


@router.get(
    path="",
    response_model=list[goal_dto.SubGoalRepsonse],
)
async def get_sub_goals(calendar_id: int):
    sub_goals = await goal_model.SubGoal.filter(calendar_id=calendar_id).all()
    return sub_goals


@router.put(
    path="/{sub_goal_id}",
    response_model=goal_dto.TopGoalResponse,
)
@atomic()
async def update_sub_goal(
    calendar_id: int, 
    sub_goal_id: int,
    form: goal_dto.TopGoalForm,
):
    sub_goal = await goal_model.SubGoal.get(
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
    result = await goal_model.SubGoal.filter(
        id=sub_goal_id,
        calendar_id=calendar_id,
    ).delete()
    return result