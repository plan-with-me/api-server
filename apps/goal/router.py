from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependency import Auth
from apps.goal import model, dto


router = APIRouter(
    prefix="",
    tags=["Goals"],
)


@router.post(
    path="/top-goals",
    dependencies=[Depends(Auth())],
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
    return dto.TopGoalResponse.from_orm(top_goal)


@router.get(
    path="/top-goals",
    dependencies=[Depends(Auth())],
    response_model=list[dto.TopGoalResponse],
)
async def get_my_top_goals(request: Request):
    request_user_id = request.state.token_payload["id"]
    top_goals = await model.TopGoal.filter(user_id=request_user_id).all()
    return [ 
        dto.TopGoalResponse.from_orm(top_goal)
        for top_goal in top_goals
    ]


@router.put(
    path="/top-goals/{top_goal_id}",
    dependencies=[Depends(Auth())],
    response_model=dto.TopGoalResponse,
)
@atomic()
async def update_top_goal(
    request: Request,
    top_goal_id: int,
    form: dto.TopGoalForm,
):
    request_user_id = request.state.token_payload["id"]
    top_goal = await model.TopGoal.get(
        id=top_goal_id,
        user_id=request_user_id,
    )
    await top_goal.update_from_dict(form.__dict__)
    return dto.TopGoalResponse.from_orm(top_goal)


@router.post(
    path="/sub-goals",
    dependencies=[Depends(Auth())],
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
    dependencies=[Depends(Auth())],
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
    dependencies=[Depends(Auth())],
    response_model=dto.SubGoalRepsonse,
)
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
