from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise import Tortoise
from tortoise.contrib.postgres.functions import Random

import pytz
from datetime import datetime, timedelta

from core.dependencies import Auth
from apps.user.model import *
from apps.goal.model import *
from apps.goal.enum import *
from apps.goal.dto import *
from apps.lounge.dto import *
from apps.lounge.query_function import *


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
    response_model=list[UserGoalsResponse],
    description="""
    유저 목록을 상위 목표, 하위 목표와 함께 조회합니다.  
    - email, tag를 둘 다 포함하지 않고 요청하면 오류가 발생합니다..  
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
            )
            .select_related("user")
            .annotate(order=Random())
            .order_by("order", "-id")
            .limit(5)
        )
        sub_goals = await SubGoal.filter(top_goal_id__in=[tg.id for tg in top_goals]).limit(100)
        for top_goal in top_goals:
            top_goal_res = TopGoalWithSubGoals(
                **top_goal.__dict__,
                sub_goals=[
                    SubGoalRepsonse(**sub_goal.__dict__) 
                    for sub_goal in sub_goals
                    if sub_goal.top_goal_id == top_goal.id
                ],
            )
            user_res = [record for record in response if record.id == top_goal.user.id]
            if user_res:
                user_res = user_res[0]
                user_res.top_goals.append(top_goal_res)
            else:
                user_res = UserGoalsResponse(**top_goal.user.__dict__)
                user_res.top_goals.append(top_goal_res)
                response.append(user_res)
        return response

    else:
        users_query_set = User.all().limit(5)
        if not email:
            raise HTTPException("Search keyword is null (email or tag)")
        users_query_set = users_query_set.filter(uid__contains=email)
        users = await users_query_set

        top_goals = await (
            TopGoal.filter(
                user_id__in=[user.id for user in users],
                show_scope=ShowScope.ALL,
            )
            .order_by("-id")
            .limit(100)
        )
        sub_goals = await SubGoal.filter(
            top_goal_id__in=[tg.id for tg in top_goals],
            created_at__gte=(now - timedelta(days=30)),
        ).limit(100)

        response = [UserGoalsResponse(**user.__dict__) for user in users]
        for top_goal in top_goals:
            top_goal_res = TopGoalWithSubGoals(
                **top_goal.__dict__, 
                sub_goals=[
                    SubGoalRepsonse(**sub_goal.__dict__) 
                    for sub_goal in sub_goals
                    if sub_goal.top_goal_id == top_goal.id
                ],
            )
            for user_res in response:
                if user_res.id == top_goal.user_id:
                    user_res.top_goals.append(top_goal_res)
        return response


@router.post(
    path="/feeds",
    response_model=list(FeedResponse),
    description="""
    개인화된 피드(다른 유저의 상위 목표)를 조회합니다.      
    exclude_ids 필드엔 제외할 상위 목표 ID 리스트를 입력합니다.(이미 UI에 노출된 상위 목표 ID 목록)   
    """
)
async def get_feeds(request: Request, form: FeedForm):
    request_user_id = request.state.token_payload["id"]
    form.exclude_ids = [str(id) for id in form.exclude_ids]
    conn = Tortoise.get_connection("default")
    main_tags = await get_tag_frequency(conn, request_user_id)

    feeds = []
    # 1. 주요 태그로 상위 목표의 tags 컬럼 검색(word_similarity 적용)
    feeds = await search_top_goals_by_tags(conn, request_user_id, main_tags, form.exclude_ids)
    if len(feeds) == 10:
        return feeds
    form.exclude_ids.extend([str(feed.top_goal.id) for feed in feeds])
    limit = 10 - len(feeds)

    # 2. 주요 태그로 상위 목표의 related_tags 컬럼 검색
    feeds.extend(
        await search_top_goals_by_tags(
            conn=conn, 
            request_user_id=request_user_id, 
            tags=main_tags, 
            exclude_ids=form.exclude_ids, 
            query_on_tags_column=False,
            limit=limit,
        )
    )
    if len(feeds) == 10:
        return feeds
    form.exclude_ids.extend([str(feed.top_goal.id) for feed in feeds])
    limit = 10 - len(feeds)

    # 3. ㅈ까고 걍 다 검색 ㅋㅋ
    top_goals = await (
        TopGoal.exclude(id__in=form.exclude_ids, user_id=request_user_id)
        .filter(show_scope=ShowScope.ALL)
        .select_related("user")
        .order_by("-id")
        .limit(limit)
    )
    feeds.extend([
        FeedResponse(
            user=UserResponse(**top_goal.user.__dict__),
            top_goal=TopGoalResponse(**top_goal.__dict__),
        ) for top_goal in top_goals
    ])
    return feeds


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
