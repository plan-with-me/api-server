from fastapi import APIRouter, Depends, status
from tortoise.transactions import atomic

from core.dependency import Auth
from apps.user import model, dto


router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.get("")
async def get_users():
    return {}
