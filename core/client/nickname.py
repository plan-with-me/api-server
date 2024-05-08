from fastapi import HTTPException

from core import aiorequests


class NicknameGenerator:

    @classmethod
    async def generate_random_nickname(
        cls, 
        max_length: int = 12,
        count: int = 30
    ):
        response = await aiorequests.get(
            url="https://nickname.hwanmoo.kr", 
            params={
                "format": "json", 
                "max_length": max_length,
                "count": count,
            },
        )
        if response.status_code != 200:
            raise HTTPException(response.status_code, response.content_text)

        return response.json()["words"]