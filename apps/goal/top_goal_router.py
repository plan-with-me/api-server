from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependency import Auth
from apps.goal import model, dto, enum
from apps.user import util as user_util


router = APIRouter(
    prefix="/top-goals",
    tags=["Top Goals"],
    dependencies=[Depends(Auth())]
)


@router.post(
    path="",
    response_model=dto.TopGoalResponse,
)
@atomic()
async def create_top_goal(
    request: Request,
    form: dto.TopGoalForm,
):
    top_goal = await model.TopGoal.create(
        **form.__dict__,
        user_id=request.state.token_payload["id"],
    )
    return top_goal


@router.get(
    path="",
    response_model=list[dto.TopGoalResponse],
    description="""
    특정 유저의 상위 목표를 조회합니다.  
    본인의 상위 목표를 조회할 경우 `user_id` 파라미터를 포함하지 않고 요청합니다.
    """,
)
async def get_top_goals(request: Request, user_id: str=None):
    request_user_id = request.state.token_payload["id"]
    query_set = model.TopGoal.filter(user_id=user_id if user_id else request_user_id)
    if user_id and user_id != request_user_id:
        query_set = query_set.filter(show_scope__not=enum.ShowScope.ME)
        if not await user_util.check_is_following(request_user_id, user_id):
            query_set = query_set.filter(show_scope__not=enum.ShowScope.FOLLWERS)
    top_goals = await query_set
    return top_goals


@router.put(
    path="/{top_goal_id}",
    response_model=dto.TopGoalResponse,
)
@atomic()
async def update_top_goal(
    request: Request,
    top_goal_id: int,
    form: dto.TopGoalForm,
):
    top_goal = await model.TopGoal.get(
        id=top_goal_id,
        user_id=request.state.token_payload["id"],
    )
    await top_goal.update_from_dict(form.__dict__)
    await top_goal.save()
    return top_goal


@router.delete(
    path="/{top_goal_id}",
    status_code=status.HTTP_200_OK,
)
@atomic()
async def delete_top_goal(request: Request, top_goal_id: int):
    result = await model.TopGoal.filter(
        id=top_goal_id,
        user_id=request.state.token_payload["id"],
    ).delete()
    return result
