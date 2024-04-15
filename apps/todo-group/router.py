from fastapi import APIRouter, Depends, status


router = APIRouter(
    prefix="/todos",
    tags=["Todo"],
)


@router.get("")
async def get_users():
    return {}
