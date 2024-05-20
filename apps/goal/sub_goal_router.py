from fastapi import APIRouter, Request, Depends, status, HTTPException

from datetime import date
from tortoise.transactions import atomic

from core.dependencies import Auth
from apps.goal import model, dto, enum
from apps.user import util as user_util


router = APIRouter(
    prefix="/sub-goals",
    tags=["User Goals"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="",
    response_model=dto.SubGoalRepsonse,
)
@atomic()
async def create_sub_goal(
    request: Request,
    top_goal_id: int,
    form: dto.SubGoalForm,
):
    request_user_id = request.state.token_payload["id"]
    top_goal = await model.TopGoal.get(id=top_goal_id)
    if top_goal.user_id != request_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    sub_goal = await model.SubGoal.create(
        **form.__dict__,
        user_id=request_user_id,
        top_goal_id=top_goal_id,
    )
    return sub_goal


@router.get(
    path="",
    response_model=list[dto.SubGoalRepsonse],
    description="""
    특정 유저의 하위 목표를 월별로 조회합니다.  
    본인의 하위 목표를 조회할 경우 `user_id` 파라미터를 포함하지 않고 요청합니다.   
    `plan_date` 파라미터는 yyyy-mm 형태로 입력하며 입력하지 않을 경우 기본값으로 현재 년-월이 입력됩니다. 
    """,
)
async def get_sub_goals(
    request: Request, 
    user_id: int = None,
    plan_date: str = date.today().strftime("%Y-%m"),
):
    request_user_id = request.state.token_payload["id"]
    query_set = model.SubGoal.filter(
        user_id=user_id if user_id else request_user_id,
        calendar_id=None,
        plan_datetime__startswith=plan_date
    )
    if user_id and user_id != request_user_id:
        query_set = query_set.filter(top_goal__show_scope__not=enum.ShowScope.ME)
        if not await user_util.check_is_following(request_user_id, user_id):
            query_set = query_set.filter(top_goal__show_scope__not=enum.ShowScope.FOLLWERS)
    sub_goals = await query_set.all()
    return sub_goals


@router.put(
    path="/{sub_goal_id}",
    response_model=dto.SubGoalRepsonse,
)
@atomic()
async def update_sub_goal(
    request: Request,
    sub_goal_id: int,
    form: dto.SubGoalForm,
):
    sub_goal = await model.SubGoal.get(
        id=sub_goal_id,
        user_id=request.state.token_payload["id"],
    )
    sub_goal.update_from_dict(form.__dict__)
    await sub_goal.save()
    return sub_goal


@router.delete(
    path="/{sub_goal_id}",
    status_code=status.HTTP_200_OK,
)
@atomic()
async def delete_sub_goal(request: Request, sub_goal_id: int):
    result = await model.SubGoal.filter(
        id=sub_goal_id,
        user_id=request.state.token_payload["id"],
    ).delete()
    return result
