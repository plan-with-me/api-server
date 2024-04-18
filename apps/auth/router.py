from typing import Union
from fastapi import APIRouter, status

from apps.auth import dto
from apps.auth import enum
from apps.user import model
from core.client.oauth import OAuthClient
from core.jwt import build_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "",
    response_model=dto.TokenResponse,
    description="로그인/회원가입 통합 API 입니다",
)
async def authentication(
    social_type: enum.SocialType, 
    credentials: Union[
        dto.GoogleCredentials, 
        dto.KakaoCredentials,
    ],
):
    if social_type == enum.SocialType.GOOGLE:
        user_info = OAuthClient.verify_google_token(credentials.id_token)
        identity_id=user_info["email"]
    elif social_type == enum.SocialType.KAKAO:
        user_info = OAuthClient.verify_kakao_token(credentials.access_token)
        identity_id=user_info["id"]
    
    user = await model.User.get_or_create(
        identity_id=identity_id,
        social_type=social_type.value,
    )
    token = build_token(
        id=user.id,
        identity_id=identity_id,
        social_type=social_type.value,
    )

    return dto.TokenResponse(access_token=token)
