import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from fastapi import status, HTTPException
from google.oauth2 import id_token
from google.auth.transport.requests import Request

from core.config import secrets


class OAuthClient:

    @classmethod
    def verify_google_token(cls, google_id_token: str):
        try:
            user_info = id_token.verify_oauth2_token(
                id_token=google_id_token,
                audience=secrets.GOOGLE_CLIENT_ID,
                request=Request(),
            )
            return user_info
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

    @classmethod
    def verify_kakao_token(cls, kakao_id_token: str):
        id_token_header = jwt.get_unverified_header(kakao_id_token)
        jwks = requests.get("https://kauth.kakao.com/.well-known/jwks.json").json()["keys"]
        jwk = [jwk for jwk in jwks if jwk["kid"] == id_token_header["kid"]][0]
        rsa_public_key = RSAAlgorithm.from_jwk(jwk)
        try:
            user_info = jwt.decode(
                jwt=kakao_id_token,
                issuer="https://kauth.kakao.com",
                audience=secrets.KAKAO_CLIENT_ID,
                algorithms=id_token_header["alg"],
                key=rsa_public_key,
                options={"verify_signature": True},
            )
            return user_info
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.__class__.__name__,
            )