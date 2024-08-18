from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic
from tortoise import Tortoise
from tortoise.expressions import RawSQL
from tortoise.contrib.postgres.functions import Random

import pytz
from datetime import datetime, timedelta

from core.dependencies import Auth
from apps.user.model import *
from apps.goal.model import *
from apps.goal.enum import *
from apps.goal.dto import *
from apps.lounge.dto import *


router = APIRouter(
    prefix="/lounge",
    tags=["Lounge"],
    dependencies=[Depends(Auth())],
)


@router.get(
    "/random-tags",
    response_model=TagsResponse,
)
async def get_random_tags(request: Request):
    result = await Tortoise.get_connection("default").execute_query_dict(f"""
        SELECT tag
        FROM (SELECT DISTINCT jsonb_array_elements_text(tags) AS tag FROM topgoal) tags
        ORDER BY RANDOM()
        LIMIT 5;
    """)
    return TagsResponse(tags=[row["tag"] for row in result])


@router.get(
    "/users",
    # response_model=list[UserGoalsResponse],
    description="""
    유저 목록을 상위 목표, 하위 목표와 함께 조회합니다.  
    - email, tag를 둘 다 포함하지 않고 요청하면 임의의 유저 목록을 조회합니다.  
    - email을 포함할 경우 이메일로 유저를 필터링합니다.  
    - tag를 포함할 경우 해당 태그의 상위 목표를 가지고 있는 유저를 필터링합니다.  
    """
)
async def get_users(
    email: str | None = None,
    tag: str | None = None,
):
    if email and tag:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only email or tag can be entered")

    now = datetime.now(tz=pytz.timezone("Asia/Seoul"))
    response = []
    if tag:
        top_goals = await (
            TopGoal.filter(
                tags__contains=[tag],
                show_scope=ShowScope.ALL,
                sub_goals__created_at__gte=(now - timedelta(days=1)),
            )
            .select_related("user")
            .prefetch_related("sub_goals")
            .annotate(order=Random())
            .order_by("order")
            .limit(10)
        )
        for top_goal in top_goals:
            user_res = UserGoalsResponse(**top_goal.user.__dict__)
            top_goal_res = TopGoalWithSubGoals(
                **top_goal.__dict__,
                sub_goals=[
                    SubGoalRepsonse(**sub_goal.__dict__) 
                    for sub_goal in top_goal.sub_goals.related_objects
                ]
            )
            user_res.top_goals.append(top_goal_res)
            response.append(user_res)
        return response

    else:
        users_query_set = User.all().limit(5)
        if email:
            users_query_set = users_query_set.filter(uid__contains=email)
        else:
            users_query_set = users_query_set.annotate(order=Random()).order_by("order")
        users = await users_query_set

        top_goals_query_set = (
            TopGoal.filter(
                user_id__in=[user.id for user in users],
                show_scope=ShowScope.ALL,
                sub_goals__created_at__gte=(now - timedelta(days=1)),
            )
            .prefetch_related("sub_goals")
            .order_by("-id")
            .limit(3)
        )
        top_goals = await top_goals_query_set

        for user in users:
            user_res = UserGoalsResponse(**user.__dict__)
            for top_goal in top_goals:
                top_goal_res = TopGoalWithSubGoals(**top_goal.__dict__)
                if user.id == top_goal.user_id:
                    top_goal_res.sub_goals = [
                        SubGoalRepsonse(**sub_goal.__dict__) 
                        for sub_goal in top_goal.sub_goals.related_objects
                    ]
                user_res.top_goals.append(top_goal_res)
            response.append(user_res)
        return response


# @router.get(
#     path="/sub-goals",
# )
# async def get_users_sub_goals(
#     request: Request,
#     user_ids: str,
# ):
#     query = (
#         "SELECT "
#         "   * "
#         "FROM ("
#         "   SELECT "
#         "       *, "
#         "       ROW_NUMBER() OVER (PARTITION BY sg.user_id ORDER BY sg.id DESC) as row_num "
#         "   FROM "
#         "       subgoal as sg "
#         "   LEFT JOIN "
#         "       topgoal tg ON tg.id = sg.top_goal_id "
#         "   WHERE "
#         "       tg.show_scope = 'all' AND sg.calendar_id IS NULL"
#         ") r "
#         "WHERE row_num <= 5 "
#     )
#     result = await SubGoal.raw(query)
#     print(result)
#     return result
