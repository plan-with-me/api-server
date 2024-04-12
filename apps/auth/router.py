from fastapi import APIRouter


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/sign-in")
async def sign_in():
    return {}
