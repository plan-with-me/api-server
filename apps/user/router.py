from fastapi import APIRouter, Depends, status


router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.get("")
async def get_users():
    return {}
