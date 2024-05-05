from typing import Union
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from tortoise.transactions import atomic

from apps.auth import dto
from apps.auth import enum
from apps.user import model
from core.client.oauth import OAuthClient
from core.client.nickname import NicknameGenerator
from core.jwt import build_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "",
    response_model=dto.TokenResponse,
    responses={
        200: {"model": dto.TokenResponse},
        201: {"model": dto.TokenResponse},
    },
    description="""
    로그인/회원가입 통합 API 입니다.  
    회원가입일 경우 응답코드는 201입니다.
    """,
)
@atomic()
async def authentication(
    social_type: enum.SocialType, 
    credentials: dto.SocialLoginCredentials,
):
    if social_type == enum.SocialType.GOOGLE:
        user_info = OAuthClient.verify_google_token(credentials.id_token)
        uid = user_info["email"]
    elif social_type == enum.SocialType.KAKAO:
        user_info = OAuthClient.verify_kakao_token(credentials.id_token)
        uid = user_info["sub"]
    
    status_code = status.HTTP_200_OK
    user = await model.User.get_or_none(
        uid=uid,
        social_type=social_type.value,
    )
    if not user:
        random_nickname = NicknameGenerator.generate_random_nickname(count=1)[0]
        status_code = status.HTTP_201_CREATED
        user = await model.User.create(
            uid=uid,
            social_type=social_type.value,
            name=random_nickname,
        )

    token = build_token(
        id=user.id,
        social_type=social_type.value,
    )

    return JSONResponse(
        status_code=status_code,
        content=dto.TokenResponse(access_token=token).__dict__,
    )


@router.get("/test")
async def test_auth():
    return build_token(id=1)
