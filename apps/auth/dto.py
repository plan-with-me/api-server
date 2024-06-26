from pydantic import BaseModel

from core.config import var_config as vars


class SocialLoginCredentials(BaseModel):
    """
    소셜 로그인/회원가입 모델
    - id_token (str): 소셜 플랫폼 인증 후 받은 ID 토큰 값
    """
    id_token: str


class TokenResponse(BaseModel):
    """
    인증 성공 시 액세스 토큰 응답 모델
    - access_token (str): API 액세스 토큰
    - token_type (str): 토큰 인증 타입
    - expires_in (str): 토큰의 유효성 지속 시간(초)
    """
    access_token: str
    token_type: str = vars.TOKEN_TYPE
    expires_in: int = vars.TOKEN_DURATION
