from typing import Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from jwt.exceptions import PyJWTError

import core.config.var_config as vars
from core.jwt import decode_token
import apps.calendar.model as calendar_model


class Auth(HTTPBearer):

    def __init__(self):
        super(Auth, self).__init__()

    async def __call__(
        self, 
        request: Request,
    ):
        try:
            token_type, token = request.headers["Authorization"].split(" ")
            if token_type != vars.TOKEN_TYPE:
                raise ValueError()
            
            token_payload = decode_token(token)
            request.state.token_payload = token_payload

        except (KeyError, ValueError, PyJWTError):
           raise HTTPException(status.HTTP_401_UNAUTHORIZED)


class CalendarPermission:

    def __init__(
        self,
        get_calendar = False,
        get_user = False,
    ) -> None:
        self.fetch_fields = []
        if get_calendar: self.fetch_fields.append("calendar")
        if get_user: self.fetch_fields.append("user")

    async def __call__(self, request: Request, calendar_id: int) -> Any:
        query_set = calendar_model.CalendarUser.filter(
            user_id=request.state.token_payload["id"],
            calendar_id=calendar_id,
        ).select_related(*self.fetch_fields).first()
        calendar_user = await query_set
        if not calendar_user:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
        request.state.calendar_user = calendar_user
