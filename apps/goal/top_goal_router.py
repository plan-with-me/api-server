from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependency import Auth
from apps.goal import model, dto


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
    return dto.TopGoalResponse.from_orm(top_goal)


@router.get(
    path="",
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
    return dto.TopGoalResponse.from_orm(top_goal)


@router.delete(
    path="/top-goals/{top_goal_id}",
    status_code=status.HTTP_200_OK,
)
@atomic()
async def delete_top_goal(request: Request, top_goal_id: int):
    result = await model.TopGoal.filter(
        id=top_goal_id,
        user_id=request.state.token_payload["id"],
    ).delete()
    return result
