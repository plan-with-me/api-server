import requests
from fastapi import HTTPException


class NicknameGenerator:

    @classmethod
    def generate_random_nickname(
        cls, 
        max_length: int = 12,
        count: int = 30
    ):
        response = requests.get(
            url="https://nickname.hwanmoo.kr", 
            params={
                "format": "json", 
                "max_length": max_length,
                "count": count,
            },
        )
        if response.status_code != 200:
            raise HTTPException(response.status_code, response.text)

        return response.json()["words"]