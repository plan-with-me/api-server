import requests
from fastapi import status, HTTPException
from google.oauth2 import id_token
from google.auth.transport.requests import Request

from apps.auth import dto
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
    def verify_kakao_token(cls, kakao_access_token):
        response = requests.get(
            url='https://kapi.kakao.com/v2/user/me?property_keys=["kakao_account.email"]',
            headers={
                "Authorization": f"Bearer {kakao_access_token}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code < 500: 
            raise HTTPException(status.HTTP_400_BAD_REQUEST, response.json())
        else:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, response.text())

