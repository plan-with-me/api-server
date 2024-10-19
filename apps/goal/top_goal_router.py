from fastapi import APIRouter, Request, Depends, status, HTTPException

from tortoise.transactions import atomic

from core.dependencies import Auth
from core.client.gpt import OpenAIClient
from apps.goal import model, dto, enum
from apps.user import util as user_util


router = APIRouter(
    prefix="/top-goals",
    tags=["User Goals"],
    dependencies=[Depends(Auth())]
)


@router.post(
    path="",
    response_model=dto.TopGoalResponse,
    description="""
    상위 목표를 생성합니다.   
    `show_scope` 필드에는 "me", "followers", "all" 값만 사용 가능합니다.   
    """
)
@atomic()
async def create_top_goal(
    request: Request,
    form: dto.TopGoalForm,
):
    if form.show_scope not in (enum.ShowScope.ME, enum.ShowScope.FOLLWERS, enum.ShowScope.ALL):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    tags = [tag.replace("#", "") for tag in list(set(form.tags))]
    if len(tags) > 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "태그는 최대 5개까지 등록 가능합니다")
    top_goal = await model.TopGoal.create(
        **form.__dict__,
        user_id=request.state.token_payload["id"],
        related_tags=OpenAIClient().get_related_tags(tags) if tags else [],
    )
    return top_goal


@router.get(
    path="",
    response_model=list[dto.TopGoalResponse],
    description="""
    특정 유저의 상위 목표를 모두 조회합니다.  
    본인의 상위 목표를 조회할 경우 `user_id` 파라미터를 포함하지 않고 요청합니다.
    """,
)
async def get_top_goals(request: Request, user_id: int = None):
    request_user_id = request.state.token_payload["id"]
    query_set = model.TopGoal.filter(
        user_id=user_id if user_id else request_user_id,
        calendar_id=None,
    )
    if user_id and user_id != request_user_id:
        query_set = query_set.filter(show_scope__not=enum.ShowScope.ME)
        if not await user_util.check_is_following(request_user_id, user_id):
            query_set = query_set.filter(show_scope__not=enum.ShowScope.FOLLWERS)
    top_goals = await query_set
    return top_goals


@router.get(
    path="/achievement-rates",
    response_model=list[dto.TopGoalAchievementRateResponse],
    description="""
    특정 유저의 상위 목표 달성률을 조회합니다.(전체 기간)
    본인의 상위 목표를 조회할 경우 `user_id` 파라미터를 포함하지 않고 요청합니다.
    """
)
async def get_top_goal_achievement_rates(
    request: Request,
    user_id: int = None,
):
    request_user_id = request.state.token_payload["id"]
    query_set = model.TopGoal.filter(
        user_id=user_id if user_id else request_user_id,
        calendar_id=None,
    )
    if user_id and user_id != request_user_id:
        query_set = query_set.filter(show_scope__not=enum.ShowScope.ME)
        if not await user_util.check_is_following(request_user_id, user_id):
            query_set = query_set.filter(show_scope__not=enum.ShowScope.FOLLWERS)
    result = await query_set.select_related("sub_goals").all()
    top_goals = list(set(result))
    sub_goals = [record.sub_goals for record in result]
    response = [
        dto.TopGoalAchievementRateResponse(**top_goal.__dict__)
        for top_goal in top_goals
    ]
    for sub_goal in sub_goals:
        if not isinstance(sub_goal, model.SubGoal):
            continue
        top_goal = [row for row in response if row.id == sub_goal.top_goal_id][0]
        top_goal.sub_goal_count += 1
        if sub_goal.status == enum.GoalStatus.COMPLETE:
            top_goal.complete_count += 1
    return response


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
    tags = [tag.replace("#", "") for tag in list(set(form.tags))]
    if tags:
        top_goal.related_tags = OpenAIClient().get_related_tags(tags)
    top_goal.update_from_dict(form.__dict__)
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
