import requests
from fastapi import status, HTTPException
from google.auth import transport

from apps.auth import dto
from core.config import secrets


class OAuthClient:

    @classmethod
    def verify_google_token(cls, id_token: str):
        try:
            user_info = id_token.verify_oauth2_token(
                id_token=id_token,
                audience=secrets.GOOGLE_CLIENT_ID,
                request=transport.requests.Request(),
            )
            return user_info
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

    @classmethod
    def verify_kakao_token(cls, form: dto.KakaoCredentials):
        response = requests.get(
            url='https://kapi.kakao.com/v2/user/me?property_keys=["kakao_account.email"]',
            headers={
                "Authorization": f"Bearer {form.access_token}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code < 500: 
            raise HTTPException(status.HTTP_400_BAD_REQUEST, response.json())
        else:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, response.text())

