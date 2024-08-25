from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependencies import Auth
from apps.goal import model, dto, enum
from apps.user import util as user_util


router = APIRouter(
    prefix="/sub-goals/{sub_goal_id}/reactions",
    tags=["Sub Goal Reaction"],
    dependencies=[Depends(Auth())],
)


@router.post(
    "",
)
@atomic()
async def create_reaction(
    request: Request,
    sub_goal_id: int, 
    form: dto.ReactionForm,
):
    reaction = await model.Reaction.create(
        **form.__dict__,
        user_id=request.state.token_payload["id"],
        sub_goal_id=sub_goal_id,
    )
    return reaction


@router.put(
    "/{reaction_id}",
)
@atomic()
async def update_reaction(
    request: Request,
    sub_goal_id: int,
    reaction_id: int,
    form: dto.ReactionForm,
):
    result = await model.Reaction.filter(
        user_id=request.state.token_payload["id"],
        reaction_id=reaction_id,
    ).update(**form.__dict__)
    return result


@router.delete(
    "/{reaction_id}",
)
@atomic()
async def delete_reaction(
    request: Request,
    sub_goal_id: int,
    reaction_id: int,
):
    result = await model.Reaction.filter(
        user_id=request.state.token_payload["id"],
        reaction_id=reaction_id,
    ).delete()
    return result
