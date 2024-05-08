from fastapi import APIRouter, Depends, Request, status, HTTPException
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.calendar import model, dto
from apps.user import model as user_models
from apps.goal import model as goal_models


router = APIRouter(
    prefix="/calendars",
    tags=["Calendar"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="",
)
@atomic()
async def create_calendars():
    pass


@router.get(
    path="",
)
async def get_calendars():
    pass
