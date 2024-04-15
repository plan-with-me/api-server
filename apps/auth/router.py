from fastapi import APIRouter, status

from apps.auth import dto
from apps.user import model
from core.client.oauth import OAuthClient
from core.jwt import build_token
from core.config import var_config as vars


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get(
    "/sign-in",
    response_model=dto.TokenResponse,
)
async def sign_in_google(credentials: dto.GoogleCredentials):
    user_info = OAuthClient.verify_google_token(credentials.id_token)
    
    user = await model.User.get_or_create(
        identity_id = user_info["email"],
    )
    token = build_token(
        id=user.id,
        identity_id=user.identity_id,
    )

    return dto.TokenResponse(access_token=token)
