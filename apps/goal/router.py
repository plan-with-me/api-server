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
    return dto.TopGoalResponse(**top_goal.__dict__)


@router.get(
    path="/top-goals",
    dependencies=[Depends(Auth())],
    response_model=list[dto.TopGoalResponse],
)
async def get_my_top_goals(request: Request):
    request_user_id = request.state.token_payload["id"]
    todo_groups = await model.TopGoal.filter(user_id=request_user_id).all()
    return [ 
        dto.TopGoalResponse(**todo_group.__dict__) 
        for todo_group in todo_groups
    ]


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
    todo = await model.SubGoal.create(
        **form.__dict__,
        user_id=request_user_id,
        top_goal_id=top_goal_id,
    )
    return dto.SubGoalRepsonse(**todo.__dict__)


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
        dto.SubGoalRepsonse(**sub_goal.__dict__)
        for sub_goal in sub_goals
    ]


@router.put(
    path="/sub-goals/{sub_goal_id}",
    dependencies=[Depends(Auth())],
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
    
