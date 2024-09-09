from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependencies import Auth
from apps.diary.model import *
from apps.diary.dto import *
from apps.user import util as user_util


router = APIRouter(
    prefix="/diaries",
    tags=["Diary"],
    dependencies=[Depends(Auth())],
)


@router.post(
    "",
    response_model=DiaryResponse,
)
@atomic()
async def create_diary(request: Request, form: DiaryForm):
    diary = await Diary.create(
        **form.__dict__,
        user_id=request.state.token_payload["id"],
    )
    return DiaryResponse(**diary.__dict__)


@router.get(
    "",
    response_model=list[DiaryResponse],
    description="""
    유저의 일기를 조회합니다.   
    - user_id가 없을 경우 본인의 일기를, 있을 경우 해당 유저의 조회 가능한 일기만 조회합니다.   
    - date가 있을 경우 해당 날짜의 일기만, 없을 경우 모든 일기를 조회합니다.   
    - date는 'yyyy-mm-dd' 형식의 문자열입니다.
    """,
)
async def get_user_diaries(
    request: Request,
    user_id: int | None = None,
    date: str | None = None
):
    request_user_id = request.state.token_payload["id"]
    query_set = Diary.filter(
        user_id=user_id if user_id else request_user_id,
    )
    if date:
        query_set = query_set.filter(date=date)
    if user_id and user_id != request_user_id:
        query_set = query_set.filter(show_scope__not=ShowScope.ME)
        if not await user_util.check_is_following(request_user_id, user_id):
            query_set = query_set.filter(show_scope__not=ShowScope.FOLLWERS)
    diaries = await query_set.select_related("user")
    return [
        DiaryResponse(
            **diary.__dict__,
            user=UserResponse(**diary.user.__dict__),
        ) for diary in diaries
    ]


@router.put(
    "/{diary_id}",
    response_model=DiaryResponse,
)
@atomic()
async def update_diary(request: Request, diary_id: int, form: DiaryForm):
    diary = await Diary.get(
        id=diary_id, 
        user_id=request.state.token_payload["id"],
    )
    diary.update_from_dict(form.__dict__)
    await diary.save()
    return DiaryResponse(**diary.__dict__)


@router.delete(
    "/{diary_id}",
)
@atomic()
async def delete_diary(request: Request, diary_id: int):
    result = await Diary.filter(
        id=diary_id,
        user_id=request.state.token_payload["id"]
    ).delete()
    return result
