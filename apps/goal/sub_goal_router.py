from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependency import Auth
from apps.goal import model, dto


router = APIRouter(
    prefix="/sub-goals",
    tags=["Sub Goals"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="/sub-goals",
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
    return dto.SubGoalRepsonse.from_orm(sub_goal)


@router.get(
    path="/sub-goals",
    response_model=list[dto.SubGoalRepsonse],
)
async def get_my_sub_goals(request: Request):
    request_user_id = request.state.token_payload["id"]
    sub_goals = await model.SubGoal.filter(
        user_id=request_user_id,
    ).all()
    return [
        dto.SubGoalRepsonse.from_orm(sub_goal)
        for sub_goal in sub_goals
    ]


@router.put(
    path="/sub-goals/{sub_goal_id}",
    response_model=dto.SubGoalRepsonse,
)
@atomic()
async def update_sub_goal(
    request: Request,
    sub_goal_id: int,
    form: dto.SubGoalForm,
):
    request_user_id = request.state.token_payload["id"]
    sub_goal = await model.SubGoal.get(
        id=sub_goal_id,
        user_id=request_user_id,
    )
    await sub_goal.update_from_dict(form.__dict__)
    return dto.SubGoalRepsonse.from_orm(sub_goal)


@router.delete(
    path="/sub-goals/{sub_goal_id}",
    status_code=status.HTTP_200_OK,
)
@atomic()
async def delete_sub_goal(request: Request, sub_goal_id: int):
    result = await model.SubGoal.filter(
        id=sub_goal_id,
        user_id=request.state.token_payload["id"],
    ).delete()
    return result
