import json
from tortoise.backends.base.client import BaseDBAsyncClient, TransactionContext

from core.config.var_config import IS_PROD
from apps.lounge.dto import *


table_prefix = '"pwm".' if IS_PROD else None


async def get_tag_frequency(
    conn: BaseDBAsyncClient | TransactionContext, 
    user_id: int,
) -> list:
    """특정 유저가 많이 소비한(사용한) 상위 목표의 태그 목록을 내림차순으로 반환합니다."""
    query = f"""
        select jsonb_array_elements_text(tags) AS tag
        from {table_prefix if IS_PROD else ''}"topgoal"
        where user_id = $1
        group by tag
        order by count(*) desc;
    """
    result = await conn.execute_query_dict(query, [user_id])
    result = [record["tag"] for record in result]
    return result


async def search_top_goals_by_tags(
    conn: BaseDBAsyncClient | TransactionContext,
    request_user_id: int,
    tags: list[str],
    exclude_ids: list[int] = [],
    limit: int = 10,
    query_on_tags_column: bool = True,
) -> list[FeedResponse]:
    """
    topgoal 테이블의 tags 필드를 기준으로 word_similarity 함수로 유사도를 측정하여
    설정한 임계값 이상의 topgoal 데이터를 필터링합니다.   
    * 알고리즘
    - tags 컬럼에 각 요소중 검색하는 태그와 유사도가 0.25 이상인 태그가 하나라도 있을 경우 포함
    - show_scope가 'all'이거나
    - show_scope가 'followers'인 경우(이 경우엔 요청 유저가 작성자를 팔로우 중일 경우에만 포함)
    - 본인 상위 목표 제외
    - 공유 달력 상위 목표 제외
    - exclude_ids에 있는 id는 제외
    - topgoal의 id를 내림차순으로 정렬
    - 최대 10개의 결과를 반환
    """
    query = f"""
    with f as (
        select target_user_id, status
        from {table_prefix if IS_PROD else ''}"follow" f 
        where user_id = {request_user_id}
    )
    select 
        t.id,
        t.created_at,
        t.updated_at,
        t.name,
        t.color,
        t.status,
        t.show_scope,
        t.tags,
        t.user_id,
        u.created_at as user_created_at,
        u.updated_at as user_updated_at,
        u.name as user_name,
        u.introduction as user_introduction,
        u.image as user_image,
        u.uid as user_uid
    from {table_prefix if IS_PROD else ''}"topgoal" t
    left join {table_prefix if IS_PROD else ''}"user" u on u.id = t.user_id
    left join f on f.target_user_id = t.user_id 
    where
        exists(
            select 1 from jsonb_array_elements_text({"tags" if query_on_tags_column else "related_tags"}) as tag
            where {
                " or ".join([
                    "public.word_similarity(decompose_korean($" + str(idx) + "), decompose_korean(tag)) >= 0.25"
                    for idx in range(1, len(tags) + 1)
                ]) if query_on_tags_column else 
                "tag in (" + ",".join(["$" + str(idx) for idx in range(1, len(tags) + 1)]) + ")"
            }
        )
        and (
            t.show_scope  = 'all'
            or (
                t.show_scope = 'followers' 
                and f.status = 'accepted'
                and t.created_at >= NOW() - INTERVAL '3 days'
            )
        )
        and t.user_id != {request_user_id}
        and t.calendar_id IS NULL
        {"and t.id not in (" + ",".join(exclude_ids) + ")" if exclude_ids else ""}
    order by t.id desc
    limit {limit}
    """
    result = await conn.execute_query_dict(query, tags)
    result = [
        FeedResponse(
            top_goal=TopGoalResponse(
                id=record["id"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
                name=record["name"],
                color=record["color"],
                status=record["status"],
                show_scope=record["show_scope"],
                user_id=record["user_id"],
                tags=json.loads(record["tags"]),
            ),
            user=UserResponse(
                id=record["user_id"],
                created_at=record["user_created_at"],
                updated_at=record["user_updated_at"],
                name=record["user_name"],
                introduction=record["user_introduction"],
                image=record["user_image"],
                uid=record["user_uid"],
            ),
        ) for record in result
    ]
    return result
